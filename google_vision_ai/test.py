from google.cloud import vision
from pdf2image import convert_from_path
import io
import csv
import os

accuracy_scores = []
client = vision.ImageAnnotatorClient()
data_dir = '../data'

# load in our csv with our manually scored data at 'data_dir/Tracking.csv'
with open(f'{data_dir}/Tracking.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)

for (student_number) in range(1, 33):
    # the csv format is index,student,a,b,c
    # get the first student (with index 1) and their a,b,c values
    student = data[student_number][1:]
    print(student)

    # student[0] is name
    # student[1] is a
    # student[2] is b
    # student[3] is c

    # we have a student number and we need to convert to a filename
    student_number = str(student_number).zfill(5)
    student_file_name = f's{student_number}.pdf'

    # load in the pdf file
    pdf_path = f'{data_dir}/{student_file_name}'

    images = convert_from_path(pdf_path, poppler_path=r'C:\Users\Engineer99\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin')
    img = images[0]

    # save image
    img_path = f'{data_dir}/{student_file_name}.jpg'
    img.save(img_path, 'JPEG')

    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations

    # show preprocessed response
    print('Preprocessed response: ')
    print(texts[0].description)
    print()

    # clean up our response
    response_data = []
    
    # split the response by new lines
    for line in texts[0].description.split('\n'):
        print(line)

        # remove all lines not containing numbers
        if not any(char.isdigit() for char in line):
            continue

        numbers = [char for char in line if char.isdigit() or char == '.']
        response_data.append(''.join(numbers))

    # show cleaned response
    print('Cleaned response: ')
    print(response_data)

    checked_a = student[1]
    checked_b = student[2]
    checked_c = student[3]

    resp_a = response_data[0]
    resp_b = response_data[1]
    resp_c = response_data[2]

    # get accuracy by comparing the checked values to the response values and assinging a 1 for correct and 0 for incorrect
    accuracy_a = 1 if checked_a == resp_a else 0
    accuracy_b = 1 if checked_b == resp_b else 0
    accuracy_c = 1 if checked_c == resp_c else 0

    # sum the accuracies and divide by 3 to get the overall accuracy
    overall_accuracy = (accuracy_a + accuracy_b + accuracy_c) / 3

    print(f'Accuracy score for {student[0]}: {overall_accuracy*100}%')

    accuracy_scores.append([student[0], overall_accuracy])

    # delete image
    os.remove(img_path)

# overall accuracy
print('---------------------------------')
overall_accuracy = sum([score[1] for score in accuracy_scores]) / len(accuracy_scores)
print(f'Overall accuracy: {overall_accuracy*100}%')

# lowest accuracy
print('---------------------------------')
lowest_accuracy = min(accuracy_scores, key=lambda x: x[1])
print(f'Lowest accuracy: {lowest_accuracy[0]} with {lowest_accuracy[1]*100}%')
print('---------------------------------')