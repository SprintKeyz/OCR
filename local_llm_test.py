import util.get_image as get_image
import util.accuracy as accuracy
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import base64
import requests
import csv
import os
import sys
import torch

# Get args
import argparse


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
            "max_new_tokens": 20
        }
        
        output_ids = self.model.generate(**inputs, **generation_args)
        output_ids = output_ids[:, inputs["input_ids"].shape[1]:]
        response = self.processor.batch_decode(output_ids, skip_special_tokens=True)
        return response
    
phi_model = Phi3VisionModel()

# Add -d flag to specify data directory
parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')
parser.add_argument('-n', '--num_students', type=int, help='number of students to process')
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

# Create an accuracy object
acc = accuracy.Accuracy()

# Save responses in the form of [student, preprocessed_response, cleaned_response]
preprocessed_responses = []
confidence_responses = []

images_arr = []

for student_number in range(1, max_students):
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
    prompt = "You are given an image. I want you to return each value next to a: b: and c: (or only a: and b: or only a: depending on what exists in the image). Return the values separated by commas WITHOUT spaces, and do not truncate numbers even if there are redundant characters. Stop once you have found the numbers (up to 3 of them), and don't try to return 'Set' anything."
    
    response = phi_model.extract_data([content], prompt)
    torch.cuda.empty_cache()
    
    # filter out everything after the letter 'S' if it exists
    response = response[0].split('S')[0]
    
    print(f"Response for image {student_number}: {response}")
    
    # split into a list of responses
    response = response.split(',')
    
    # append to accuracy calculation
    acc.append_calculation(student, response)
    
acc.print_report()

# print accuracy report to "report_{i}.txt" depending on how many reports exist (i should be the next number)
i = 0
while os.path.exists(f"report_{i}.txt"):
    i += 1
    
with open(f"report_{i}.txt", "w") as f:
    f.write(acc.return_report_as_string())
    print(f"Report saved to report_{i}.txt")
    f.close()