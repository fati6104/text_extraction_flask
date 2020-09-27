from docx2python import docx2python
import docx
import pandas as pd
import tempfile
import uuid
import os

UPLOAD_FOLDER = 'static/uploads'

fll = str(uuid.uuid4())

def getText(path,filename):
    doc = docx.Document(path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
        f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','w')
        f.write('\n'.join(fullText))
        f.close()
    print('Done')
    

#getText('../samples/sample2.docx')






