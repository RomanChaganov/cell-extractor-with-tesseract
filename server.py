import numpy as np
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from io import BytesIO
from PIL import Image, ImageOps
from scripts.process_image_start_point import process_image
import sys
import shutil
import os

sys.path.insert(0, 'scripts')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    

def generate_table(pairs):
    text_list = ['<table>', '<tr>', '<th>Ключ</th>', '<th>Значение</th>', '</tr>']
            
    accum = []
    for key, value in pairs:
        if not key:
            accum.append(value)
            continue
            
        if len(accum) != 0:
            text_list.append('<tr>')
            text = '\n'.join(accum)
            accum = []
            text_list.append(f'<td></td>')
            text_list.append(f'<td>{text}</td>')
            text_list.append('</tr>')
            
        text_list.append('<tr>')
        text_list.append(f'<td>{key}</td>')
        text_list.append(f'<td>{value}</td>')
        text_list.append('</tr>')
    
    text_list.append('</table>')
    return text_list


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
    pairs = process_image(image)
    
    pairs = generate_table(pairs)
    
    with open('bin/pairs.txt', 'w', encoding='utf-8') as f:
        f.writelines(pairs)
    
    shutil.make_archive('excel_tables', 'zip', 'excel')

    return send_file('excel_tables.zip', as_attachment=True)
    
    
@app.route('/get_size', methods=['GET'])
def get_size():
    dir_path = 'bin/rotated_tables'
    size = len(os.listdir(dir_path))
    return jsonify({'size': size})
    
    
@app.route('/bin/<path:filename>', methods=['GET'])
def get_image(filename):
    return send_file('bin/' + filename)
    

# @app.route('/download', methods=['GET'])
# def download():
#     return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
