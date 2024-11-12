from google.cloud import vision
import csv
import os
import sys
import requests
import base64
from secrets_1 import openai_api_key as api_key

import util.accuracy as accuracy
import util.get_image as get_image

from compare import compare_and_choose

# get args
import argparse

# add -d flag to specify data directory
parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')
parser.add_argument('-n', '--num_students', type=int, help='number of students to process')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-ev', '--extra-verbose', action='store_true', help='extra verbose output')

args = parser.parse_args()

if args.extra_verbose:
    args.verbose = True

if not args.data:
    print('Please specify a data directory with -d')
    sys.exit()

client = vision.ImageAnnotatorClient()

# create an accuracy object
acc = accuracy.Accuracy()

# save responses in the form of [student, preprocessed_response, cleaned_response]
preprocessed_responses = []
confidence_responses = []

data_dir = args.data

# load in our csv with our manually scored data at 'data_dir/Tracking.csv'
with open(f'{data_dir}/Tracking.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    
# get num of files in data directory
num_files = len([name for name in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, name))]) - 1
    
max_students = args.num_students if args.num_students else num_files

# get the last value on line 0 to get the "answer indicator"
answer_indicator = data[0][-1]

for (student_number) in range(1, max_students):
    student = data[student_number][1:]
    
    # the csv format is index,student,a,b,c
    # get the first student (with index 1) and their a,b,c values
    
    sys.stdout.write(f'\rProcessing student {student_number}/{max_students}...             ')
    sys.stdout.flush()

    content = get_image.process_image(data_dir, student_number)

    image = vision.Image(content=content)
    text_detection_params = vision.TextDetectionParams(enable_text_detection_confidence_score=True)
    image_context = vision.ImageContext(text_detection_params=text_detection_params)
    response = client.text_detection(image=image, image_context=image_context)

    texts = response.text_annotations
    
    if (args.verbose):
        print()
        print(f'Student: {student}')
        
    if (args.extra_verbose):
        print()
        print('Texts:')
        for text in texts:
            print(text.description)
        print()
        
    if not texts:
        print(f'No text found for student {student_number}')
        continue
    
    # grab confidence for student
    confidence_responses.append([student, texts[0].confidence])

    # clean up our response
    response_data = []
    
    # split the response by new lines
    for line in texts[0].description.split('\n'):
        # replace letter Z with number 2
        old_line = line
        
        # remove the text "write only answers below this line"
        if answer_indicator.lower() in line.lower():
            line = line.replace(answer_indicator, '')
            
        # if the line has the word "Set" in it, remove the entire line
        if 'Set' in line:
            continue
        
        line = line.replace('Z', '2')
        line = line.replace('z', '2')
        line = line.replace('|', '1')
        line = line.replace('니', '4')
        line = line.replace('५', '4')
        line = line.replace('S', '5')
        line = line.replace('s', '5')
        
        if (args.extra_verbose):
            print(f'Old line: {old_line}')
            print(f'New line: {line}')
        
        # remove all lines not containing numbers
        if not any(char.isdigit() for char in line):
            continue

        numbers = [char for char in line if char.isdigit() or char == '.']
        response_data.append(''.join(numbers))

    vision_response = response_data
    
    
    
    
    
    
    
    
    
    
    # now try openAI
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
        
    chatgpt_response = response_data
    
    print('\nActual response:', student[1:])
    print('Vision response:', vision_response)
    print('ChatGPT response:', chatgpt_response)
    
    # compare the two responses and choose the best one
    chosen_response = compare_and_choose(vision_response, chatgpt_response)
    
    print('Chosen response:', chosen_response)
        
    # append our calculation
    acc.append_calculation(student, chosen_response, args.verbose)
    
acc.print_report()