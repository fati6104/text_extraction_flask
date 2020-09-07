#from tabula import read_pdf
import PyPDF2
import os
import subprocess
import uuid
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from PIL import Image
from PyPDF2 import PdfFileReader, generic
import zlib

UPLOAD_FOLDER = 'static/uploads'

fll = str(uuid.uuid4())

def get_color_mode(obj):

    try:
        cspace = obj['/ColorSpace']
    except KeyError:
        return None

    if cspace == '/DeviceRGB':
        return "RGB"
    elif cspace == '/DeviceCMYK':
        return "CMYK"
    elif cspace == '/DeviceGray':
        return "P"

    if isinstance(cspace, generic.ArrayObject) and cspace[0] == '/ICCBased':
        color_map = obj['/ColorSpace'][1].getObject()['/N']
        if color_map == 1:
            return "P"
        elif color_map == 3:
            return "RGB"
        elif color_map == 4:
            return "CMYK"

def get_object_images(x_obj):
    images = []
    for obj_name in x_obj:
        sub_obj = x_obj[obj_name]

        if '/Resources' in sub_obj and '/XObject' in sub_obj['/Resources']:
            images += get_object_images(sub_obj['/Resources']['/XObject'].getObject())

        elif sub_obj['/Subtype'] == '/Image':
            zlib_compressed = '/FlateDecode' in sub_obj.get('/Filter', '')
            if zlib_compressed:
               sub_obj._data = zlib.decompress(sub_obj._data)

            images.append((
                get_color_mode(sub_obj),
                (sub_obj['/Width'], sub_obj['/Height']),
                sub_obj._data
            ))

    return images

def get_pdf_images(pdf_fp):
    images = []
    pdf_in = PdfFileReader(pdf_fp)
    lm = pdf_in.numPages
    for p_n in range(lm):
        page = pdf_in.getPage(p_n)
        try:
            page_x_obj = page['/Resources']['/XObject'].getObject()
        except KeyError:
            continue
        images += get_object_images(page_x_obj)
    return images

def pdf(pdf_path,filename):
    #df = read_pdf(pdf_path , pages='all')
    pdfReader = PyPDF2.PdfFileReader(pdf_path)
    pp = pdfReader.numPages
    print('Number of pages : '+ str(pp))
    for i in range(0 , pp ):
        pageObj = pdfReader.getPage(i)
        page = pageObj.extractText()
        f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','a')
        f.write(page)
        #f.write(str(df))
        f.close()
    ind = 0
    for image in get_pdf_images(pdf_path):
      if image is None:
        pass
      else:
        (mode, size, data) = image
        img = Image.open(StringIO(data))
        img.save(os.path.join(UPLOAD_FOLDER+filename)+'.jpg')
        ind = ind + 1


#pdf('../samples/sampleimage.pdf')

