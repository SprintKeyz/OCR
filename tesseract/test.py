from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Engineer99\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
print(pytesseract.image_to_string(Image.open('../test.jpg')))