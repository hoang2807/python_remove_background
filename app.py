import os
import time
from dotenv import load_dotenv

from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS

from werkzeug.utils import secure_filename

from bg_remove import BGRemove
import base64
from io import BytesIO
from PIL import Image
from waitress import serve

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
root = os.path.split(os.path.abspath(__file__))[0]
ckpt_image = 'pretrained/modnet_photographic_portrait_matting.ckpt'
bg_remover = BGRemove(ckpt_image)

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])

TEMPLATE_FOLDER = os.path.join(root, 'web_solution', 'template')
STATIC_FOLDER = os.path.join(root, 'web_solution', 'static')
STATIC_IMAGE_PATH = os.path.join(root, 'web_solution', 'static', 'images')

UPLOAD_FOLDER = os.path.join(STATIC_IMAGE_PATH, 'test_images')
RESULT_IMAGE = os.path.join(STATIC_IMAGE_PATH, 'result_images')

make_directory = [os.makedirs(path,exist_ok=True) for path in [UPLOAD_FOLDER, RESULT_IMAGE]]

app = Flask(__name__, template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)
cors = CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = 'PrinceAPI'


SWAGGER = 'swagger.html'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/remove_background', methods=['GET', 'POST'])
def remove_background():
    if request.method == 'POST':
        print('header: ', request.headers['Authorization'])
        print(os.environ.get('API_KEY'))
        if request.headers['Authorization'] != os.environ.get('API_KEY'):
            return jsonify({'message': 'Invalid Authorization'}), 400
        if 'files[]' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400

        files = request.files.getlist('files[]')
        errors = {}
        file = files[0]
        filename = ""
        
        if file and allowed_file(file.filename):
            ts = time.time()
            filename = f"{str(ts)}-{file.filename}"
            filename = secure_filename(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            base64_string = process(filename)
            data = {
                'img_base64': "data:image/png;base64,"+base64_string
            }
            print('filename: ', filename)
            print(filename.rsplit('.', 1)[0]+'.png')
            os.remove(os.path.join(UPLOAD_FOLDER, filename))
            os.remove(os.path.join(RESULT_IMAGE, filename.rsplit('.', 1)[0]+'.png'))
            
            return jsonify(data), 200
        else:
            errors['message'] = 'File type is not allowed'
    return render_template('swagger_ui.html')

@app.route('/spec')
def get_spec():
    return send_from_directory(app.root_path, 'swagger.yaml')

def process(input_filename):
    image = os.path.join(UPLOAD_FOLDER, input_filename)
    output_filename = bg_remover.image(
        image, background=False, output=RESULT_IMAGE, save=True)

    img = Image.open(os.path.join(RESULT_IMAGE, output_filename))
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    im_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return im_base64

if __name__ == '__main__':
    # app.run(debug=False, host='0.0.0.0', port=5000)
    serve(app, host='127.0.0.1', port=5000)
