# get -d arg as directory

import argparse

parser = argparse.ArgumentParser(description='OCR Processing.')
parser.add_argument('-d', '--data', type=str, help='data directory')

args = parser.parse_args()

if not args.data:
    print('Please specify a data directory with -d')
    sys.exit()
    
data_dir = args.data

# for each file in data directory, rename it to s{file number)}.pdf, with file number being 5 digits
# ex. a.pdf -> s00001.pdf

import os

for i, filename in enumerate(os.listdir(data_dir)):
    if filename.endswith('.pdf'):
        os.rename(f'{data_dir}/{filename}', f'{data_dir}/s{(i+1):05}.pdf')
        
print('Files renamed successfully.')