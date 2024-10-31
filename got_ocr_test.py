from transformers import AutoModel, AutoTokenizer
import os
import argparse
import csv
import sys
import util.get_image as get_image
import util.accuracy as accuracy
import torch

tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()

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

# get the last value on line 0 to get the "answer indicator"
answer_indicator = data[0][-1]

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
    img_path = get_image.process_image_as_file(data_dir, data, student_number)
    response = model.chat_crop(tokenizer, img_path, ocr_type='ocr')
    os.remove(img_path)
    
    torch.cuda.empty_cache()
    
    print("\n\n\n\n")
    print(f"Preprocessed response for {student[0]} (id {student_number}): ", response)
    print("\n\n\n\n")
    
acc.print_report()

# print accuracy report to "report_{i}.txt" depending on how many reports exist (i should be the next number)
i = 0
while os.path.exists(f"report_{i}.txt"):
    i += 1
    
with open(f"report_{i}.txt", "w") as f:
    f.write(acc.return_report_as_string())
    print(f"Report saved to report_{i}.txt")
    f.close()

# input your test image
image_file = 'test.jpg'

# plain texts OCR
res = model.chat(tokenizer, image_file, ocr_type='ocr')

# format texts OCR:
# res = model.chat(tokenizer, image_file, ocr_type='format')

# fine-grained OCR:
# res = model.chat(tokenizer, image_file, ocr_type='ocr', ocr_box='')
# res = model.chat(tokenizer, image_file, ocr_type='format', ocr_box='')
# res = model.chat(tokenizer, image_file, ocr_type='ocr', ocr_color='')
# res = model.chat(tokenizer, image_file, ocr_type='format', ocr_color='')

# multi-crop OCR:
# res = model.chat_crop(tokenizer, image_file, ocr_type='ocr')
# res = model.chat_crop(tokenizer, image_file, ocr_type='format')

# render the formatted OCR results:
# res = model.chat(tokenizer, image_file, ocr_type='format', render=True, save_render_file = './demo.html')

print(res)
