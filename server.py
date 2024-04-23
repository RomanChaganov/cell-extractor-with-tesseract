from flask import Flask, render_template, request
from io import BytesIO
from PIL import Image

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
    image.save('processed_image.jpg')
    return 'Данные успешно обработаны'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
