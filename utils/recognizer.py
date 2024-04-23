import random
import numpy as np
from PIL import Image, ImageDraw
from tesserocr import PyTessBaseAPI, OEM, RIL, PSM


LANG='rus+eng'
OEM_TYPE=OEM.LSTM_ONLY
mode_to_ril = {'blocks': RIL.BLOCK, 'lines': RIL.TEXTLINE, 'words': RIL.WORD}


def color_range_replace(img_arr, start_range=(0, 0, 150),
                        color_repl=(255, 255, 255)):
    color = (img_arr > start_range).all(axis=-1)
    img_arr[color] = color_repl
    return img_arr
    
    
def get_blocks(image, mode='blocks'):   
    with PyTessBaseAPI(lang=LANG, psm=PSM.AUTO, oem=OEM_TYPE) as api:
        api.SetImage(image)
        boxes = api.GetComponentImages(mode_to_ril[mode], True)
    return boxes
    
    
def generate_random_color(num):
    random.seed(num)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color = (r, g, b, 128)
    return color
    
    
def rectangle_draw(image, boxes):
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, 'RGBA')
    for (im, box, block_id, par_id) in boxes:
        rect = (box['x'], box['y'], box['w'] + box['x'], box['h'] + box['y'])
        color = generate_random_color(block_id)
        draw.rectangle(rect, fill=color)
    result = Image.alpha_composite(image, overlay)
    return result


def recognize(image, mode='blocks', color_repl=True):
    if color_repl:
        img_arr = np.array(image)
        img_arr = color_range_replace(img_arr)
        image = Image.fromarray(img_arr)
       
    boxes = get_blocks(image, mode)
    image = image.convert('RGBA')
    image = rectangle_draw(image, boxes)
        
    return image
    