import sys
import cv2
import numpy as np
import pytesseract
import pandas as pd
from generate_table import generate_table


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
    # inverted_image = cv2.bitwise_not(image)
    # cv2.imshow('result', resized_image)
    # cv2.waitKey()
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
    # cv2.imshow('result', combined_image)
    # cv2.waitKey()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    combined_image_dilated = cv2.dilate(combined_image, kernel, iterations=2)
    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.bitwise_not(resized_image)
    image_without_lines = cv2.subtract(resized_image, combined_image_dilated)
    result = cv2.bitwise_not(image_without_lines)
    # cv2.imshow('result', image_without_lines)
    # cv2.waitKey()
    return result

def word_search(image, image_output):
    kernel = np.ones((2, 3), np.uint8)
    # image_temp = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=3)
    #kernel = np.ones((1, 5), np.uint8)
    #image_temp = cv2.dilate(image, kernel, iterations=3)
    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    text = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cropped = image_output[y:y+h, x:x+w]
        if cropped.shape[0] == 0 or cropped.shape[1] == 0:
            break
        cropped = cv2.copyMakeBorder(cropped, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        #cropped = cv2.resize(cropped, (cropped.shape[1] * 3, cropped.shape[0] * 3))
        #cv2.imshow('cell', cropped)
        #cv2.waitKey()
        text.append(get_text(cropped))
    text.reverse()
    text = ''.join(text)
    return image_output, ' '.join(text.split())


def get_text(image):
    text = pytesseract.image_to_string(image, config='-l rus+eng --oem 1 --psm 7')
    return text


if __name__ == '__main__':
    image = load_image(sys.argv[1])
    resized_image = resize_image(image)
    thresh = binarization_image(resized_image)
    image_without_lines = remove_table_lines(thresh, resized_image)
    # image_without_lines = cv2.bitwise_not(image_without_lines)
    contours = get_contours(thresh)
    cropped = None
    mask = np.zeros(thresh.shape, dtype=np.uint8)
    cells = []
    for contour in contours:
        #cv2.drawContours(resized_image, [contour], -1, (255, 255, 255), -1)
        # mask = np.zeros(thresh.shape, dtype=np.uint8)
        x, y, w, h = cv2.boundingRect(contour)
        #print(x, y, w, h)
        # cropped, text = word_search(image_without_lines[y:y+h, x:x+w], resized_image[y:y+h, x:x+w])
        text = get_text(image_without_lines[y:y+h, x:x+w])
        cells.append((x, y, x + w, y + h, text))
        print(text)
        #print(cropped.shape)
        #mask = np.zeros(resized_image.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        cropped = cv2.bitwise_and(image_without_lines, mask)
        cropped[mask == 0] = 255
        # cv2.imshow('cell', cropped)
        # cv2.waitKey(160)
        #exit()
    generate_table(cells)
    cv2.imshow('invert', cropped)
    cv2.waitKey()