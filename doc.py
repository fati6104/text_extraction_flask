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
    doc_result = docx2python(path)
    res = pd.DataFrame(doc_result.body[1][1:]).\
                            applymap(lambda val: val[0].strip("\t"))
    type(doc_result.images) # dict
    doc_result.images.keys() # dict_keys(['image1.png'])
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
        f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','a')
        f.write('\n'.join(fullText))
        f.write(str(res))
        f.close()
    for key,val in doc_result.images.items():
        f = open(key, "wb")
        f.write(val)
        f.close()
    print('Done')
    

#getText('../samples/sample2.docx')






