import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('../test.jpg')
print(result)