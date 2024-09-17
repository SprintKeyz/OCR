from google.cloud import vision
from pdf2image import convert_from_path
import io
import csv
import os
import sys

import util.accuracy as accuracy
import util.get_image as get_image

client = vision.ImageAnnotatorClient()

# create an accuracy object
acc = accuracy.Accuracy()

# save responses in the form of [student, preprocessed_response, cleaned_response]
preprocessed_responses = []
confidence_responses = []

data_dir = './data'

# load in our csv with our manually scored data at 'data_dir/Tracking.csv'
with open(f'{data_dir}/Tracking.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    
max_students = 5

for (student_number) in range(1, max_students):
    student = data[student_number][1:]
    
    # the csv format is index,student,a,b,c
    # get the first student (with index 1) and their a,b,c values
    
    sys.stdout.write(f'\rProcessing student {student_number}/{max_students}...             ')
    sys.stdout.flush()

    content = get_image.process_image(data_dir, data, student_number)

    image = vision.Image(content=content)
    text_detection_params = vision.TextDetectionParams(enable_text_detection_confidence_score=True)
    image_context = vision.ImageContext(text_detection_params=text_detection_params)
    response = client.text_detection(image=image, image_context=image_context)

    texts = response.text_annotations
    
    # grab confidence for student
    confidence_responses.append([student, texts[0].confidence])

    # clean up our response
    response_data = []
    
    # split the response by new lines
    for line in texts[0].description.split('\n'):
        # remove all lines not containing numbers
        if not any(char.isdigit() for char in line):
            continue

        numbers = [char for char in line if char.isdigit() or char == '.']
        response_data.append(''.join(numbers))

    # save cleaned response
    preprocessed_responses.append([student, texts[0].description, response_data])
    
    # append our calculation
    acc.append_calculation(student, response_data)

# overall accuracy
print()
print()
print('---------------------------------')
print(f'Overall word accuracy: {acc.get_overall_word_accuracy() * 100}%')
print(f'Overall character accuracy: {acc.get_overall_character_accuracy() * 100}%')
print('---------------------------------')
print(f'Minimum word accuracy: {acc.get_min_word_accuracy()[0]}, {acc.get_min_word_accuracy()[1] * 100}%')
print(f'Minimum character accuracy: {acc.get_min_character_accuracy()[0]}, {acc.get_min_character_accuracy()[1] * 100}%')
print('---------------------------------')
if len(acc.get_most_common_skipped_characters()) > 0:
    print(f'Most common skipped characters: {acc.get_most_common_skipped_characters()[0][0]}, {acc.get_most_common_skipped_characters()[0][1]} times')
if len(acc.get_most_common_ghost_characters()) > 0:
    print(f'Most common ghost characters: {acc.get_most_common_ghost_characters()[0][0]}, {acc.get_most_common_ghost_characters()[0][1]} times')
print('---------------------------------')

# print response data for a student
def get_response_data(student_name):
    for response in preprocessed_responses:
        if response[0][0] == student_name:
            return response