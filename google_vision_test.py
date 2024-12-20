from google.cloud import vision
import csv
import os
import sys

import util.accuracy as accuracy
import util.get_image as get_image

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
        
    if (args.verbose):
        print()
        print(f'Cleaned response: {response_data}')
        print()

    # save cleaned response
    preprocessed_responses.append([student, texts[0].description, response_data])
    
    # append our calculation
    acc.append_calculation(student, response_data, args.verbose)
    
acc.print_report()