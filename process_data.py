# get -d arg as directory

import argparse
import sys

parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')
parser.add_argument('-s', '--start', type=int, help='start index')

start_index = 1

args = parser.parse_args()

if args.start:
    start_index = args.start

if not args.data:
    print('Please specify a data directory with -d')
    sys.exit()
    
data_dir = args.data

y_n = input(f'Are you sure you want to rename all files in {data_dir}? (y/n): ')

if y_n.lower() != 'y':
    print('Exiting...')
    sys.exit()

# for each file in data directory, rename it to s{file number)}.pdf, with file number being 5 digits
# ex. a.pdf -> s00001.pdf

import os

for i, filename in enumerate(os.listdir(data_dir)):
    if filename.endswith('.pdf'):
        os.rename(f'{data_dir}/{filename}', f'{data_dir}/s{(i+start_index):05}.pdf')
        
print('Files renamed successfully.')