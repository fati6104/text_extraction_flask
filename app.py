import os
from flask import Flask, render_template,request,Response,redirect, url_for, send_from_directory,send_file
from werkzeug.utils import secure_filename
from doc_image import doc_image
from excel import excel
from pdf import pdf,get_color_mode,get_object_images,get_pdf_images
from doc import getText
from scene_image import image_scene
from cv_extract import fileformat,pdf2txt,get_color_mode,get_object_images,get_pdf_images,image_cv,PhoneNo,email,skills,name,company,city,degree,uni,language,hobby,convert_list_to_string,save,cr_db,insert_data,sv_db,cr_tb,art_media,educ,info,bio_heal,fin_com,csv_art,csv_edu,csv_info,csv_bio,csv_fin
import csv

UPLOAD_FOLDER = 'static/uploads/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'tif', 'mp4', 'pdf', 'xlsx', 'docx'])

cr_db()
cr_tb()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        select = request.form.get('format')
        if file.filename == '':
          return render_template('upload.html', msg='No file selected')
        if str(select) == 'pdf':
          if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            pdf(os.path.join(app.config['UPLOAD_FOLDER'],file.filename),file.filename)
            return send_file(UPLOAD_FOLDER+file.filename+'.txt',as_attachment=True)
        if str(select) == 'doc':
          if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            getText(os.path.join(app.config['UPLOAD_FOLDER'],file.filename),file.filename)
            return send_file(UPLOAD_FOLDER+file.filename+'.txt',as_attachment=True)
        if str(select) == 'excel':
          if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            excel(os.path.join(app.config['UPLOAD_FOLDER'],file.filename),file.filename)
            return send_file(UPLOAD_FOLDER+file.filename+'.txt',as_attachment=True)
        if str(select) == 'sc_image':
          if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            image_scene(os.path.join(app.config['UPLOAD_FOLDER'],file.filename),file.filename)
            return send_file(UPLOAD_FOLDER+file.filename+'.txt',as_attachment=True)
        else :
          if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            doc_image(os.path.join(app.config['UPLOAD_FOLDER'], file.filename),file.filename)
            return send_file(UPLOAD_FOLDER+file.filename+'.txt', as_attachment=True)
    elif request.method == 'GET':
        return render_template('upload.html')



@app.route('/data_cv', methods=['GET', 'POST'])
def data_cv():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('cv')
        select = request.form.get('sv_m')
        pf = request.form.get('pro')
        if str(select) == 'csv':
            with open(UPLOAD_FOLDER+'cv_file.csv', 'w', newline='') as ou:
                writer = csv.writer(ou)
                writer.writerow(["Name", "Email", "Phone","City","Skills","University","Degree","Company","Language","Hobby","Profile"])
            for f in uploaded_files:
                filename = secure_filename(f.filename)
                image_cv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                save(os.path.join(app.config['UPLOAD_FOLDER'], filename),filename)
            if str(pf) == 'art':
                csv_art()
                return send_file(UPLOAD_FOLDER+'cv_art.csv', as_attachment=True)
            if str(pf) == 'fin':
                csv_fin()
                return send_file(UPLOAD_FOLDER+'cv_fin.csv', as_attachment=True)
            if str(pf) == 'bio':
                csv_bio()
                return send_file(UPLOAD_FOLDER+'cv_bio.csv', as_attachment=True)
            if str(pf) == 'info':
                csv_info()
                return send_file(UPLOAD_FOLDER+'cv_info.csv', as_attachment=True)
            if str(pf) == 'ens':
                csv_edu()
                return send_file(UPLOAD_FOLDER+'cv_ens.csv', as_attachment=True)
        else:
            for f in uploaded_files:
                root_dir = os.path.dirname(os.getcwd())
                filename = secure_filename(f.filename)
                image_cv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                sv_db(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if str(pf) == 'art':
                art_media()
                os.system('mysqldump --login-path=local cvv_db cv_art > '+UPLOAD_FOLDER+'art.sql')
                return send_file(UPLOAD_FOLDER+'art.sql', as_attachment=True)
            if str(pf) == 'fin':
                fin_com()
                os.system('mysqldump --login-path=local cvv_db cv_fin > '+UPLOAD_FOLDER+'finance.sql')
                return send_file(UPLOAD_FOLDER+'finance.sql', as_attachment=True)
            if str(pf) == 'bio':
                bio_heal()
                os.system('mysqldump --login-path=local cvv_db cv_bio > '+UPLOAD_FOLDER+'health.sql')
                return send_file(UPLOAD_FOLDER+'health.sql', as_attachment=True)
            if str(pf) == 'info':
                info()
                os.system('mysqldump --login-path=local cvv_db cv_info > '+UPLOAD_FOLDER+'informatique.sql')
                return send_file(UPLOAD_FOLDER+'informatique.sql', as_attachment=True)
            if str(pf) == 'ens':
                educ()
                os.system('mysqldump --login-path=local cvv_db cv_educ > '+UPLOAD_FOLDER+'education.sql')
                return send_file(UPLOAD_FOLDER+'education.sql', as_attachment=True)
    elif request.method == 'GET':
        return render_template('cv.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
   return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run()

