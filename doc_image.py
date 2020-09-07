from PIL import Image
import pytesseract
from PyPDF2 import PdfFileWriter
import uuid
import io
import os

UPLOAD_FOLDER = 'static/uploads/'

def doc_image(path,filename):
  text = ''
  text = pytesseract.image_to_string(Image.open(path))
  f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','w')
  f.write(text)
  f.close()


