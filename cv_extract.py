from tabula import read_pdf
from PIL import Image
import subprocess
import fnmatch                        #fnmatch function is used to match the string 
import os
from PyPDF2 import PdfFileWriter
import PyPDF2
import re
import json
import collections
import spacy
import pandas as panda
import en_core_web_sm
import fr_core_news_sm
import csv
import uuid
import pandas as pd
from PIL import Image
from spacy.matcher import Matcher
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from PyPDF2 import PdfFileReader, generic
import zlib
import mysql.connector
from mysql.connector import errorcode
import datetime
import configparser
import time
import getpass

UPLOAD_FOLDER = 'static/uploads/'
databases = ("cvv_db")

def fileformat(path):
    for file in os.listdir(path):         #path = current directory path
        if fnmatch.fnmatch(file, '*.docx'):
            return docx
        elif fnmatch.fnmatch(file, '*.pdf'):
            return PyPDF2
        elif fnmatch.fnmatch(file, '*.rtf'):
            return rtf
        elif fnmatch.fnmatch(file, '*.zip'):
            return zip


def pdf2txt(path):
    #fl = open(path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(path,'rb')
    nop = pdfReader.getNumPages()
    extractedtxt =""
    for i in range(nop):
        pageObj = pdfReader.getPage(i)
        extractedtxt += pageObj.extractText()
    #fl.close()
    return extractedtxt

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

def get_pdf_images(path):
    images = []
    pdf_in = PdfFileReader(path)
    lm = pdf_in.numPages
    for p_n in range(lm):
        page = pdf_in.getPage(p_n)
        try:
            page_x_obj = page['/Resources']['/XObject'].getObject()
        except KeyError:
            continue
        images += get_object_images(page_x_obj)
    return images


def PhoneNo(path):
    text = pdf2txt(path)
    pattern = re.compile(r'[\d]{2}.[\d]{2}.[\d]{2}.[\d]{2}.[\d]{2}')
    match = pattern.findall(text)
    if match:
        number = ''.join(match[0])
        if len(number) > 10:
            return  number
        else:
            return number

def email(path):
    tmp = pdf2txt(path)
    pattern=re.compile(r'[a-zA-Z0-9-\.]+@+[a-zA-Z0-9-\.]*')
    matches=pattern.findall(tmp)
    mail = ''
    for i in matches:
        mail = mail + i
    return mail

def skills(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('results'), 'technical_skills.csv'))
    skills = list(data.columns.values)
    skill_set = []
    for token in tokens:
        if token.lower() in skills:
            skill_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in skills:
            skill_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skill_set])]

def name(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'name.csv'),encoding ='latin1')
    names = list(data.columns.values)
    name_set = []
    for token in tokens:
        if token.lower() in names:
            name_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in names:
            name_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in name_set])]

def company(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'company.csv'),encoding ='latin1')
    companies = list(data.columns.values)
    company_set = []
    for token in tokens:
        if token.lower() in companies:
            company_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in companies:
            company_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in company_set])]

def city(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'cities.csv'),encoding ='latin1')
    cities = list(data.columns.values)
    city_set = []
    for token in tokens:
        if token.lower() in cities:
            city_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in cities:
            city_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in city_set])]

def degree(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'degree.csv'),encoding ='latin1')
    degrees = list(data.columns.values)
    degree_set = []
    for token in tokens:
        if token.lower() in degrees:
            degree_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in degrees:
            degree_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in degree_set])]

def uni(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'uni.csv'),encoding ='latin1')
    unis = list(data.columns.values)
    uni_set = []
    for token in tokens:
        if token.lower() in unis:
            uni_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in unis:
            uni_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in uni_set])]

def language(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'language.csv'),encoding ='latin1')
    languages = list(data.columns.values)
    language_set = []
    for token in tokens:
        if token.lower() in languages:
            language_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in languages:
            language_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in language_set])]


def hobby(path):
    nlp = en_core_web_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'hobbies.csv'),encoding ='latin1')
    hobbies = list(data.columns.values)
    hobby_set = []
    for token in tokens:
        if token.lower() in hobbies:
            hobby_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in hobbies:
            hobby_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in hobby_set])]

def profile(path):
    nlp = fr_core_news_sm.load()
    my_text = nlp(pdf2txt(path))
    nounchunks = list(my_text.noun_chunks)
    tokens = [token.text for token in my_text if not token.is_stop]
    data = panda.read_csv(os.path.join(os.path.dirname('data'), 'profile.csv'),encoding ='latin1')
    profiles = list(data.columns.values)
    profile_set = []
    for token in tokens:
        if token.lower() in profiles:
            profile_set.append(token)
    for token in nounchunks:
        token = token.text.lower().strip()
        if token in profiles:
            profile_set.append(token)
    return [i.capitalize() for i in set([i.lower() for i in profile_set])]

def convert_list_to_string(org_list, seperator=' '):
    return seperator.join(org_list)


def image_cv(path):
    fll = str(uuid.uuid4())
    for image in get_pdf_images(path):
        (mode, size, data) = image
        img = Image.open(StringIO(data))
        try:
            img.save("photo/"+convert_list_to_string(name(path))+".jpg")
        except:
            img.save("photo/unknown"+fll+".jpg")
        break

#SAVE DATA IN CSV FILE

def save(path,filename):
    with open(os.path.join(UPLOAD_FOLDER)+'cv_file.csv', 'a', newline='') as ou:
        writer = csv.writer(ou)
        writer.writerow([convert_list_to_string(name(path)),email(path),PhoneNo(path),convert_list_to_string(city(path)),convert_list_to_string(skills(path)),convert_list_to_string(uni(path)),convert_list_to_string(degree(path)),convert_list_to_string(company(path)),convert_list_to_string(language(path)),convert_list_to_string(hobby(path)),convert_list_to_string(profile(path))])


def csv_art():
    with open(UPLOAD_FOLDER+'cv_file.csv','r') as fin, open (UPLOAD_FOLDER+'cv_art.csv','w') as fout:
        read = csv.reader(fin)
        headers = next(read)
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)            
        for row in csv.reader(fin, delimiter=','):
            if row[10] == 'Artiste' or row[10] == 'Musicien' or row[10] == 'Musicienne' or row[10] == 'Idol' or row[10] == 'RédactioN' or row[10] == 'Rédacteur' or row[10] == 'Journaliste' or row[10] == 'Modérateur' or row[10] == 'Modératrice' or row[10] == 'Conseillère' or row[10] == 'Producteur' or row[10] == 'Productrice' or row[10] == 'Production' or row[10] == 'Production':
                writer.writerow(row)

def csv_fin():
    with open(UPLOAD_FOLDER+'cv_file.csv','r') as fin, open (UPLOAD_FOLDER+'cv_fin.csv','w') as fout:
        read = csv.reader(fin)
        headers = next(read)
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)            
        for row in csv.reader(fin, delimiter=','):
            if row[10] == 'Financier' or row[10] == 'Financière' or row[10] == 'Commercial' or row[10] == 'Commerciale' or row[10] == 'Comptable' or row[10] == 'Comptabilité' or row[10] == 'Gestionnaire' or row[10] == 'Analyste' or row[10] == 'Assistant' or row[10] == 'Assistante':
                writer.writerow(row)

def csv_bio():
    with open(UPLOAD_FOLDER+'cv_file.csv','r') as fin, open (UPLOAD_FOLDER+'cv_bio.csv','w') as fout:
        read = csv.reader(fin)
        headers = next(read)
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)            
        for row in csv.reader(fin, delimiter=','):
            if row[10] == 'Biologiste' or row[10] == 'Infermier' or row[10] == 'Infermière' or row[10] == 'Docteur' or row[10] == 'Médecin' or row[10] == 'Chirurgien' or row[10] == 'Chirurgienne' or row[10] == 'Pharmacien' or row[10] == 'Pharmacienne':
                writer.writerow(row)


def csv_info():
    with open(UPLOAD_FOLDER+'cv_file.csv','r') as fin, open (UPLOAD_FOLDER+'cv_info.csv','w') as fout:
        read = csv.reader(fin)
        headers = next(read)
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)            
        for row in csv.reader(fin, delimiter=','):
            if row[10] == 'Développeur' or row[10] == 'Développeuse' or row[10] == 'Technicien' or row[10] == 'Technicienne' or row[10] == 'Ingénieur':
                writer.writerow(row)


def csv_edu():
    with open(UPLOAD_FOLDER+'cv_file.csv','r') as fin, open (UPLOAD_FOLDER+'cv_ens.csv','w') as fout:
        read = csv.reader(fin)
        headers = next(read)
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)            
        for row in csv.reader(fin, delimiter=','):
            if row[10] == 'Enseignant' or row[10] == 'Enseignante' or row[10] == 'Prof' or row[10] == 'Professeur':
                writer.writerow(row)


#SAVE DATA IN MySQL DB FILE

def cr_db():
    db_connection = mysql.connector.connect(host= "localhost",user= "root",passwd= "root")
    try:
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE DATABASE cvv_db")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errors.DatabaseError:
            print("already exists.")

def cr_tb():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")



def insert_data(n, em,ph,ci,sk,un,d,comp,lan,ho,pr):
    query = ("INSERT INTO cv "
         "(name,email,phone_num,city,competences,universite,diplome,entreprise,langue,loisirs,profile) "
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    args = (n, em,ph,ci,sk,un,d,comp,lan,ho,pr)
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query, args)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()




def sv_db(path):
    a = convert_list_to_string(name(path))
    b = email(path)
    c = PhoneNo(path)
    d = convert_list_to_string(city(path))
    e = convert_list_to_string(skills(path))
    f = convert_list_to_string(uni(path))
    g = convert_list_to_string(degree(path))
    h = convert_list_to_string(company(path))
    i = convert_list_to_string(language(path))
    j = convert_list_to_string(hobby(path))
    k = convert_list_to_string(profile(path))
    insert_data(a,b,c,d,e,f,g,h,i,j,k)


def art_media():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv_art (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")

    query = ("INSERT INTO cv_art "
         "SELECT * "
         "FROM cv "
         "WHERE profile IN ('artiste','musicien','musicienne','idol','rédaction','rédactrice','rédacteur','journaliste','modérateur','conseiller','modératrice','conseillère','producteur','productrice','production','peintre')")
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()
        #os.popen("mysqldump --login-path=local %s cv_art > %s.sql" % (databases,UPLOAD_FOLDER+"cv_art"))


def fin_com():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv_fin (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")

    query = ("INSERT INTO cv_fin "
         "SELECT * "
         "FROM cv "
         "WHERE profile IN ('financier','financière','commercial','commerciale','comptable','comptabilité','gestionnaire','analyste','assistant','assistante')")
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()



def bio_heal():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv_bio (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")

    query = ("INSERT INTO cv_bio "
         "SELECT * "
         "FROM cv "
         "WHERE profile IN ('biologiste','infermier','infermière','docteur','médecin','chirurgien','chirurgienne','pharmacien','pharmacienne')")
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()


def info():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv_info (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")

    query = ("INSERT INTO cv_info "
         "SELECT * "
         "FROM cv "
         "WHERE profile IN ('développeur','développeuse','technicien','technicienne','ingénieur')")
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()


def educ():
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute("CREATE TABLE cv_educ (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,name varchar(200),email TEXT,phone_num TEXT,city varchar(25),competences TEXT,universite TEXT,diplome TEXT,entreprise TEXT,langue TEXT,loisirs TEXT,profile TEXT)")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")

    query = ("INSERT INTO cv_educ "
         "SELECT * "
         "FROM cv "
         "WHERE profile IN ('enseignant','enseignante','prof','professeur')")
    try:
        db_connection = mysql.connector.connect(host="localhost",user="root",passwd="root",database="cvv_db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(query)
        if db_cursor.lastrowid:
            print('last insert id', db_cursor.lastrowid)
        else:
            print('last insert id not found')
        db_connection.commit()
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.close()


