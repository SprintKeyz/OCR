from google.cloud import vision
from pdf2image import convert_from_path
import io
import csv
import os

# for our metrics
accuracy_scores = [] # a percentage of correct answers
skipped_characters = [] # a list of characters that were skipped
ghost_characters = [] # a list of characters that were added but are not in the original document
character_accuracy = [] # a percentage of correct characters


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

    # crop our image by pixels
    # 38, 1856 is point 1
    # 731, 2292 is point 2

    # crop image
    img = img.crop((38, 1856, 731, 2292))

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

    # check for any skipped characters and append the character that was skipped
    skipped_chars_a = [char for char in checked_a if char not in resp_a]
    skipped_chars_b = [char for char in checked_b if char not in resp_b]
    skipped_chars_c = [char for char in checked_c if char not in resp_c]
    skipped_chars = skipped_chars_a + skipped_chars_b + skipped_chars_c
    print(f'Skipped characters: {skipped_chars}')
    skipped_characters.append([student[0], skipped_chars])

    # check for any ghost characters and append the character that was added
    ghost_chars_a = [char for char in resp_a if char not in checked_a]
    ghost_chars_b = [char for char in resp_b if char not in checked_b]
    ghost_chars_c = [char for char in resp_c if char not in checked_c]
    ghost_chars = ghost_chars_a + ghost_chars_b + ghost_chars_c
    print(f'Ghost characters: {ghost_chars}')
    ghost_characters.append([student[0], ghost_chars])

    # get the character accuracy by comparing the checked values to the response values and assinging a 1 for correct and 0 for incorrect
    char_accuracy_a = sum([1 if checked_a[i] == resp_a[i] else 0 for i in range(min(len(checked_a), len(resp_a)))]) / min(len(checked_a), len(resp_a))
    char_accuracy_b = sum([1 if checked_b[i] == resp_b[i] else 0 for i in range(min(len(checked_b), len(resp_b)))]) / min(len(checked_b), len(resp_b))
    char_accuracy_c = sum([1 if checked_c[i] == resp_c[i] else 0 for i in range(min(len(checked_c), len(resp_c)))]) / min(len(checked_c), len(resp_c))
    overall_char_accuracy = (char_accuracy_a + char_accuracy_b + char_accuracy_c) / 3
    print(f'Character accuracy for {student[0]}: {overall_char_accuracy*100}%')
    character_accuracy.append([student[0], overall_char_accuracy])

    # delete image
    os.remove(img_path)

# overall accuracy
print()
print('---------------------------------')
overall_accuracy = sum([score[1] for score in accuracy_scores]) / len(accuracy_scores)
print(f'Overall word accuracy: {overall_accuracy*100}%')
overall_char_accuracy = sum([score[1] for score in character_accuracy]) / len(character_accuracy)
print(f'Overall character accuracy: {overall_char_accuracy*100}%')
print('---------------------------------')

# lowest accuracy
lowest_accuracy = min(accuracy_scores, key=lambda x: x[1])
print(f'Lowest accuracy: {lowest_accuracy[0]} with {lowest_accuracy[1]*100}%')
# get most commonly missed characters
most_common_skipped_characters = {}
for student in skipped_characters:
    for char in student[1]:
        if char in most_common_skipped_characters:
            most_common_skipped_characters[char] += 1
        else:
            most_common_skipped_characters[char] = 1
most_common_skipped_characters = sorted(most_common_skipped_characters.items(), key=lambda x: x[1], reverse=True)
print(f'Number of skipped characters: {len(most_common_skipped_characters)}')
print(f'Most commonly skipped characters: {most_common_skipped_characters}')
# get ghost characters
most_common_ghost_characters = {}
for student in ghost_characters:
    for char in student[1]:
        if char in most_common_ghost_characters:
            most_common_ghost_characters[char] += 1
        else:
            most_common_ghost_characters[char] = 1
most_common_ghost_characters = sorted(most_common_ghost_characters.items(), key=lambda x: x[1], reverse=True)
print(f'Number of ghost characters: {len(most_common_ghost_characters)}')
print(f'Most common ghost characters: {most_common_ghost_characters}')
print('---------------------------------')