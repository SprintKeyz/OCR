from pdf2image import convert_from_path
import io
import os

def process_image(data_dir, students_data, student_number, popp_path=r'C:\Users\Engineer99\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin'):
    student = students_data[student_number][1:]
    
    student_number = str(student_number).zfill(5)
    student_file_name = f's{student_number}.pdf'
    
    pdf_path = f'{data_dir}/{student_file_name}'
    
    images = convert_from_path(pdf_path, poppler_path=popp_path)
    img = images[0]
    
    # crop image
    img = img.crop((38, 1856, 731, 2292))
    
    # save image
    img_path = f'{data_dir}/{student_file_name}.jpg'
    img.save(img_path, 'JPEG')
    
    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()
        
    os.remove(img_path)
        
    return content