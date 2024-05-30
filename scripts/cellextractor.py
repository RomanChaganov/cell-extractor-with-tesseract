import os
import shutil
import cv2
import numpy as np
from scripts.generate_table import generate_table
from scripts.config import TESSDATA_PATH
from tesserocr import PyTessBaseAPI, OEM, RIL, PSM
from PIL import Image


def load_image(file_name):
    image = cv2.imread(file_name)
    if image is None:
        raise ValueError("Файл не прочитан!")
    return image


def resize_image(image, new_width=1600):
    height, width = image.shape[0], image.shape[1]
    ratio = width / height
    new_height = int(new_width / ratio)
    return cv2.resize(image, (new_width, new_height))


def binarization_image(image, block_size=15):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, 5)
    return thresh


def get_contours(thresh, max_area=50000, min_area=1000):
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    cells_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < max_area and area > min_area:
            cells_contours.append(contour)
    return cells_contours


def remove_table_lines(image, resized_image):
    hor = np.array([[1, 1, 1, 1, 1, 1, 1]])
    vertical_lines_eroded_image = cv2.erode(image, hor, iterations=10)
    vertical_lines_eroded_image = cv2.dilate(vertical_lines_eroded_image, hor, iterations=10)
    ver = np.array([[1],
                    [1],
                    [1],
                    [1],
                    [1],
                    [1],
                    [1]])
    horizontal_lines_eroded_image = cv2.erode(image, ver, iterations=10)
    horizontal_lines_eroded_image = cv2.dilate(horizontal_lines_eroded_image, ver, iterations=10)
    combined_image = cv2.add(vertical_lines_eroded_image, horizontal_lines_eroded_image)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    combined_image_dilated = cv2.dilate(combined_image, kernel, iterations=2)
    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.bitwise_not(resized_image)
    image_without_lines = cv2.subtract(resized_image, combined_image_dilated)
    result = cv2.bitwise_not(image_without_lines)
    return result


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


def generate_tables(table_name, number):
    image = load_image(table_name)
    resized_image = resize_image(image)
    thresh = binarization_image(resized_image)
    image_without_lines = remove_table_lines(thresh, resized_image)
    contours = get_contours(thresh)
    mask = np.zeros(thresh.shape, dtype=np.uint8)
    cells = []
    api = PyTessBaseAPI(lang='rus+eng', psm=PSM.SINGLE_BLOCK, oem=OEM.TESSERACT_LSTM_COMBINED, path=TESSDATA_PATH)

    if os.path.exists(f'cells{number}'):
        shutil.rmtree(f'cells{number}')
    os.makedirs(f'cells{number}')

    cell_id = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cropped = image_without_lines[y:y+h, x:x+w]
        cv2.imwrite(f'cells{number}/cell{cell_id}.jpg', cropped)
        cell_id += 1
        text = get_text(api, cropped)
        cells.append((x, y, x + w, y + h, text))
        # print(text)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        cropped = cv2.bitwise_and(image_without_lines, mask)
        cropped[mask == 0] = 255
    api.End()
    generate_table(cells, number)
