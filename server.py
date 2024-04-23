import numpy as np
from flask import Flask, render_template, request, send_file
from io import BytesIO
from PIL import Image, ImageOps
from scripts.process_image_start_point import process_image
import sys
import shutil

sys.path.insert(0, 'scripts')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    mode = request.form.get('mode')
    file = request.files.get('file')
    
    if not file:
        return 'Данные отсутствуют или повреждены'
        
    image = Image.open(BytesIO(file.read()))
    image = image.convert('RGB')
    image = ImageOps.exif_transpose(image)
    image = np.array(image)
    process_image(image)
    shutil.make_archive('excel_tables', 'zip', 'excel')

    return "Успешно"


# @app.route('/download', methods=['GET'])
# def download():
#     return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
