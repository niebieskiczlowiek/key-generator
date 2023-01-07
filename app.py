from flask import Flask, render_template, request, redirect, send_file, after_this_request
from funcs import generate_keypair
from werkzeug.utils import secure_filename
import os, glob
from funcs import signFile, verifyFile

app = Flask(__name__)

UPLOAD_FOLDER = 'keys'
UPLOAD_FOLDER2 = 'recieved'
ALLOWED_EXTENSIONS = {'pem', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2

def clear_folder(folder):
    try:
        files = glob.glob(f'{folder}/*')
        for file in files:
            os.remove(file)
    except:
        pass


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/generating", methods=['GET', 'POST'])
def generating():
    return render_template('generating.html')

@app.route('/signing', methods=['GET', 'POST'])
def signing():
    return render_template('signing.html')

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    clear_folder('keys')
    return redirect("/")

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    generate_keypair()
    return redirect("/download")

@app.route('/download', methods=['GET', 'POST'])
def download():
    return render_template('download.html')

@app.route('/get_private', methods=['GET', 'POST'])
def get_private():
    key_path = 'keys/private.pem'

    return send_file(key_path)

@app.route('/get_public', methods=['GET', 'POST'])
def get_public():
    key_path = 'keys/public.pem'
    return send_file(key_path)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    print("siema siema")
    if request.method == 'POST':
        # check if the post request has the file part
        f = request.files['file']
        if f.filename != 'private.pem' or f.filename != 'public.pem':
            message = 'Import failed'
            return render_template('upload.html', message=message)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return redirect('/upload')
    else:
        return redirect('/upload')


@app.route('/list', methods=['GET', 'POST'])
def list():
    keys = os.listdir('keys')
    if len(keys) == 0:
        message = "No keys found"
    else:
        message = "Current active keys:"
    return render_template('view.html', keys=keys, message=message)

@app.route('/sign', methods=['GET', 'POST'])
def sign():
    return render_template('sign.html')

@app.route('/signer', methods=['GET', 'POST'])
def signer():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER2'], secure_filename(f.filename)))
        file = 'recieved/' + secure_filename(f.filename)

        public_key = open('keys/public.pem', 'rb').read()
        private_key = open('keys/private.pem', 'rb').read()

        sig = signFile(private_key, public_key, file)
        w = open('recieved/signed.pem', 'wb')
        w.write(sig)
        w.close()
        signed = 'recieved/signed.pem'

        @after_this_request
        def purge(response):
            try:
                clear_folder('recieved')
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        return send_file(signed)
    else:
        return redirect('/sign')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    return render_template('verifying.html')

@app.route('/verifier', methods=['GET', 'POST'])
def verifier():
    # ogFile, sigFile, key = request.form['file1'], request.form['file2'], request.form['file3']
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        ogFile, sigFile, key = uploaded_files

        ogFile.save(os.path.join(app.config['UPLOAD_FOLDER2'], secure_filename(ogFile.filename)))
        sigFile.save(os.path.join(app.config['UPLOAD_FOLDER2'], secure_filename(sigFile.filename)))
        key.save(os.path.join(app.config['UPLOAD_FOLDER2'], secure_filename(key.filename)))

        file = 'recieved/' + secure_filename(ogFile.filename)
        signature = 'recieved/' + secure_filename(sigFile.filename)
        key = 'recieved/' + secure_filename(key.filename)

        

        try: 
            if verifyFile(key, signature, file):
                message = "Verification passed"
            else:
                message = "Verification failed"
        except:
            message = "Verification failed"
            
        @after_this_request
        def purge(response):
            try:
                clear_folder('recieved')
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        return render_template('verifying.html', message=message)
    else:
        return redirect('/verify')

if __name__ == "__main__":
        app.run(debug=True)