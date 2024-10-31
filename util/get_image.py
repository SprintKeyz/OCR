from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import io
import os

def process_image(data_dir, student_number, popp_path=r'C:\Users\Engineer99\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin'):
    
    student_number = str(student_number).zfill(5)
    student_file_name = f's{student_number}.pdf'
    
    pdf_path = f'{data_dir}/{student_file_name}'
    
    images = convert_from_path(pdf_path, poppler_path=popp_path)
    img = images[0]
    
    # resize to 1654x2341
    img = img.resize((1654, 2341))
    
    # crop image
    img = img.crop((38, 1856, 731, 2292))
    
    # increase contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)
    
    # save image
    img_path = f'{data_dir}/{student_file_name}.jpg'
    img.save(img_path, 'JPEG')
    
    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()
        
    os.remove(img_path)
        
    return content

def process_image_as_pil(data_dir, students_data, student_number, popp_path=r'C:\Users\Engineer99\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin'):
    student = students_data[student_number][1:]
    
    student_number = str(student_number).zfill(5)
    student_file_name = f's{student_number}.pdf'
    
    pdf_path = f'{data_dir}/{student_file_name}'
    
    images = convert_from_path(pdf_path, poppler_path=popp_path)
    img = images[0]
    
    # resize to 1654x2341
    img = img.resize((1654, 2341))
    
    # crop image
    img = img.crop((38, 1856, 731, 2292))
    
    # increase contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)
    
    # decrease resolution
    scalar = 0.9
    img = img.resize((int(img.size[0] * scalar), int(img.size[1] * scalar)))
    
    return img

def process_image_as_file(data_dir, students_data, student_number, popp_path=r'C:\Users\Engineer99\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin'):
    student = students_data[student_number][1:]
    
    student_number = str(student_number).zfill(5)
    student_file_name = f's{student_number}.pdf'
    
    pdf_path = f'{data_dir}/{student_file_name}'
    
    images = convert_from_path(pdf_path, poppler_path=popp_path)
    img = images[0]
    
    # resize to 1654x2341
    img = img.resize((1654, 2341))
    
    # crop image
    img = img.crop((38, 1856, 731, 2292))
    
    # increase contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)
    
    # decrease resolution
    scalar = 0.9
    img = img.resize((int(img.size[0] * scalar), int(img.size[1] * scalar)))
    
    # save image
    img_path = f'{data_dir}/{student_file_name}.jpg'
    img.save(img_path, 'JPEG')
    
    return img_path