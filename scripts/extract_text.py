from tesserocr import PyTessBaseAPI, OEM, RIL, PSM
from PIL import Image
from scripts.get_pair import get_pair


def get_text(api, image):
    image = Image.fromarray(image)
    api.SetImage(image)
    text = api.GetUTF8Text()
    # text_list = []
    # words = api.GetWords()
    # for word in words:
    #     api.SetImage(word[0])
    #     text_list.append(api.GetUTF8Text())
    return text


def extract_text(image):
    pairs = []
    api = PyTessBaseAPI(lang='rus+eng', psm=PSM.AUTO, oem=OEM.TESSERACT_LSTM_COMBINED, path=r'D:\Program\Tesseract-OCR\tessdata')
    text = get_text(api, image)
    texts = [i for i in text.split('\n') if i]
    for text in texts:
        pairs.append(get_pair(text))
    api.End()
    return pairs
