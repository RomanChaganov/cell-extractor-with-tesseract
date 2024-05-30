from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
from utils import recognizer
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/upload', methods=['POST'])
def upload():
    mode = request.form.get('mode')
    file = request.files.get('file')
    
    if not file:
        return 'Данные отсутствуют или повреждены'
        
    image = Image.open(BytesIO(file.read()))
    image = image.convert('RGB')
    image = ImageOps.exif_transpose(image)
    image = recognizer.recognize(image, mode, color_repl=False)
    
    img_file = BytesIO()
    image = image.convert('RGB')
    image.save(img_file, 'JPEG')
    img_file.seek(0)
    return send_file(img_file, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
