from google.cloud import vision
import csv
import os
import sys
import argparse

# Import utility modules
import util.get_image as get_image

# Get command line arguments
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

# Prepare to collect tracking data
tracking_data = [["id", "student", "a", "b", "c", "Write ONLY answers below this line"]]

# Determine number of files in data directory
num_files = len([name for name in os.listdir(args.data) if os.path.isfile(os.path.join(args.data, name))]) - 1
max_students = args.num_students if args.num_students else num_files

for student_number in range(1, max_students + 1):
    sys.stdout.write(f'\rProcessing student {student_number}/{max_students}...             ')
    sys.stdout.flush()

    # Process the image for the current student
    content = get_image.process_image(args.data, student_number)  # Adjust this call as needed
    image = vision.Image(content=content)
    text_detection_params = vision.TextDetectionParams(enable_text_detection_confidence_score=True)
    image_context = vision.ImageContext(text_detection_params=text_detection_params)
    response = client.text_detection(image=image, image_context=image_context)

    texts = response.text_annotations

    if texts:
        detected_answers = texts[0].description.split('\n')
        cleaned_answers = []

        # Clean the detected answers
        for line in detected_answers:
            line = line.strip()
            line = line.replace('Z', '2').replace('z', '2').replace('|', '1')
            line = line.replace('니', '4').replace('५', '4')
            line = line.replace('S', '5').replace('s', '5')

            if any(char.isdigit() for char in line):
                cleaned_answers.append(''.join(char for char in line if char.isdigit() or char == '.'))

        # Create row for CSV (filling empty values as needed)
        tracking_row = [student_number, f'Student {student_number}']  # Placeholder for student name
        tracking_row.extend(cleaned_answers[:3])  # Limit to first 3 answers
        tracking_row.append("Write ONLY answers below this line")  # Placeholder text
        
        # Fill remaining answers with empty strings if less than 3
        while len(tracking_row) < 6:
            tracking_row.insert(-1, '')  # Insert empty string before the placeholder text
        
        tracking_data.append(tracking_row)

# Write the tracking data to a new CSV file
with open(f'{args.data}/Tracking.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(tracking_data)

print("\nTracking.csv has been generated successfully.")
