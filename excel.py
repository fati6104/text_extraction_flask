import pandas as pd
import os

UPLOAD_FOLDER = 'static/uploads/'

def excel(path,filename):
	df = pd.read_excel (path)
	f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','w')
	f.write(str(df))
	f.close()

