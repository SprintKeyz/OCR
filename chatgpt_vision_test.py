import base64
import requests

import secrets_1 as secrets
import util.get_image as get_image
import util.accuracy as accuracy
import util.benchmark as benchmark

api_key = secrets.openai_api_key

from pdf2image import convert_from_path
import io
import csv
import os
import sys

# get args
import argparse

# add -d flag to specify data directory
parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')
parser.add_argument('-n', '--num_students', type=int, help='number of students to process')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

args = parser.parse_args()

if not args.data:
    print('Please specify a data directory with -d')
    sys.exit()
    
data_dir = args.data

# load in our csv with our manually scored data at 'data_dir/Tracking.csv'
with open(f'{data_dir}/Tracking.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    
# get num of files in data directory
num_files = len([name for name in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, name))]) - 1
    
max_students = args.num_students if args.num_students else num_files

# create an accuracy object
acc = accuracy.Accuracy()

# save responses in the form of [student, preprocessed_response, cleaned_response]
preprocessed_responses = []
confidence_responses = []

for (student_number) in range(1, max_students):
    # the csv format is index,student,a,b,c
    # get the first student (with index 1) and their a,b,c values
    student = data[student_number][1:]

    # student[0] is name
    # student[1] is a
    # student[2] is b
    # student[3] is c

    # we have a student number and we need to convert to a filename
    sys.stdout.write(f'\rProcessing student {student_number}/{max_students}...             ')
    sys.stdout.flush()

    content = get_image.process_image(data_dir, data, student_number)
    content = base64.b64encode(content).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
        'model': 'gpt-4o-mini',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Find all numbers in this image and return them each on a new line, unless the word "Set" is before the number. Do not return ANYTHING except the numbers. You should also always return three lines, since there will always be 3 numbers!'
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
        
        if (args.verbose):
            print(f'Old line: {old_line}')
            print(f'New line: {line}')
        
        # remove all lines not containing numbers
        if not any(char.isdigit() for char in line):
            continue

        numbers = [char for char in line if char.isdigit() or char == '.']
        response_data.append(''.join(numbers))
        
    if (args.verbose):
        print()
        print(f'Cleaned response: {response_data}')
        print()
    
    # append our calculation
    acc.append_calculation(student, response_data)
    
acc.print_report()