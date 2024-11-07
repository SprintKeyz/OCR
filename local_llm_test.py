import util.get_image as get_image
import util.accuracy as accuracy
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import torch.nn.functional as F
import base64
import requests
import csv
import os
import sys
import torch

# Get args
import argparse

import secrets_1 as secrets
api_key = secrets.openai_api_key


class Phi3VisionModel:
    def __init__(self, model_id="microsoft/Phi-3-vision-128k-instruct", device="cuda"):
        self.model_id = model_id
        self.device = device
        self.model = self.load_model()
        self.processor = self.load_processor()
        torch.cuda.empty_cache()
        
    def load_model(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="cuda:0",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            _attn_implementation="flash_attention_2"
        )
        model = torch.compile(model) # Compile the model
        return model.to(self.device)  # Ensure model is on GPU
    
    def load_processor(self):
        return AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
    
    def extract_data(self, image_data, prompt):
        formatted_prompt = f"<|user|>"
        for i in range (len(image_data)):
            formatted_prompt += f"\n<|image_{i+1}|>"
            
        formatted_prompt += f"\n{prompt}\n<|end|>\n<|assistant|>"
        inputs = self.processor(formatted_prompt, image_data, return_tensors="pt", padding=True).to(self.device)  # Move inputs to GPU
        
        generation_args = {
            "do_sample": False,
            "max_new_tokens": 18,
        }
        
        output = self.model.generate(**inputs, **generation_args, output_scores=True, return_dict_in_generate=True)
        output_ids = output.sequences[:, inputs["input_ids"].shape[1]:]
        response = self.processor.batch_decode(output_ids, skip_special_tokens=True)
        
        # Calculate confidence scores
        logits = output.scores
        probs = [F.softmax(logit, dim=-1) for logit in logits]
        confidences = [prob.max().item() for prob in probs]
        
        return response, confidences
    
phi_model = Phi3VisionModel()

# Add -d flag to specify data directory
parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')
parser.add_argument('-n', '--num_students', type=int, help='number of students to process')
parser.add_argument('-s', '--start_index', type=int, help='index of student to start at')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

args = parser.parse_args()

if not args.data:
    print('Please specify a data directory with -d')
    sys.exit()

data_dir = args.data

# Load in our CSV with our manually scored data at 'data_dir/Tracking.csv'
with open(f'{data_dir}/Tracking.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    
# Get num of files in data directory
num_files = len([name for name in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, name))]) - 1
    
max_students = args.num_students if args.num_students else num_files

start_index = args.start_index if args.start_index else 1

if start_index > num_files:
    print('Start index is greater than number of files in data directory')
    sys.exit()

# Create an accuracy object
acc = accuracy.Accuracy()

# Save responses in the form of [student, preprocessed_response, cleaned_response]
preprocessed_responses = []
confidence_responses = []

images_arr = []

for student_number in range(start_index, max_students + start_index):
    # The CSV format is index,student,a,b,c
    # Get the first student (with index 1) and their a,b,c values
    student = data[student_number][1:]

    # student[0] is name
    # student[1] is a
    # student[2] is b
    # student[3] is c

    sys.stdout.write(f'\rProcessing student {student_number}/{max_students}...             ')
    sys.stdout.flush()
    content = get_image.process_image_as_pil(data_dir, data, student_number)
    prompt = (
        "Extract the answers labeled 'a:', 'b:', and 'c:' from the document. "
        "Only return the answers in a comma-separated format ((WITHOUT SPACES)) with (NO extra text). "
    )
    
    response, confidence = phi_model.extract_data([content], prompt)
    torch.cuda.empty_cache()
    
    print(f"Preprocessed response for {student[0]} (id {student_number}): ", response)
    print(f"Confidence for {student[0]} (id {student_number}): ", confidence)
    
    # if any value in the confidence array is less than 0.6, pass to GPT4
    if any([c < 0.7 for c in confidence]):
        print("--------------- Delegating to OpenAI! ------------------")
        
        content = get_image.process_image(data_dir, student_number)
        content = base64.b64encode(content).decode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            'model': 'gpt-4o',
            'temperature': 0,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': "Extract all answers from this image and return each on a new line. The image contains bedly written handwriting, and contains no commas. Return NOTHING except the answers, and do not include any letters in the answers. If you find answers 1 and 2, return '1,2' followed by a new line."
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{content}'
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 100,
        }

        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
        response_json = response.json()
        
        #print(response_json)

        content_data = response_json['choices'][0]['message']['content']

        # clean up our response
        response_data = []
        
        # split the response by new lines
        for line in content_data.split('\n'):
            # if a line starts with "Set" or "set", ignore the first 5 characters
            if line.lower().startswith('set'):
                line = line[5:]
                
            # replace letter Z with number 2
            old_line = line
            line = line.replace('Z', '2')
            line = line.replace('z', '2')
            line = line.replace('|', '1')
            
            # remove the text "write only answers below this line"
            if 'write only answers below this line' in line.lower():
                line = line.replace('Write ONLY answers below this line', '')
                
            line = line.replace('S', '5')
            line = line.replace('s', '5')
            
            # remove all lines not containing numbers
            if not any(char.isdigit() for char in line):
                continue
            
            numbers = [char for char in line if char.isdigit() or char == '.']
            response_data.append(''.join(numbers))
            
        acc.append_calculation(student, response_data)
        
    else:
        # filter out everything after the first space
        response = response[0].split(' ')[0]
        
        # remove % symbols
        response = response.replace('%', '')
        
        # replace '(' with a 1
        response = response.replace('(', '1')
        response = response.replace('C', '6')
        
        # if we have a trailing comma, remove it
        if response[-1] == ',':
            response = response[:-1]
        
        #print(f"Processed response for {student[0]} (id {student_number}): ", response)
        
        # split into a list of responses
        response = response.split(',')
        
        # append to accuracy calculation
        acc.append_calculation(student, response)
    
    print('\n\n\n\n\n')
    
acc.print_report()

# print accuracy report to "report_{i}.txt" depending on how many reports exist (i should be the next number)
i = 0
while os.path.exists(f"report_{i}.txt"):
    i += 1
    
with open(f"report_{i}.txt", "w") as f:
    f.write(acc.return_report_as_string())
    print(f"Report saved to report_{i}.txt")
    f.close()