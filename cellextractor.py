import sys
import cv2
import numpy as np
import pytesseract


def load_image(file_name):
    image = cv2.imread(file_name)
    if image is None:
        raise ValueError("Файл не прочитан!")
    return image


def resize_image(image, new_width=1550):
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


def word_search(image, image_output):
    kernel = np.ones((2, 3), np.uint8)
    image_temp = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=3)
    #kernel = np.ones((1, 5), np.uint8)
    #image_temp = cv2.dilate(image, kernel, iterations=3)
    contours = cv2.findContours(image_temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    text = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cropped = image_output[y-4:y+h, x-1:x+w]
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
    contours = get_contours(thresh)
    cropped = None
    mask = np.zeros(thresh.shape, dtype=np.uint8)
    # masks = []
    for contour in contours:
        #cv2.drawContours(resized_image, [contour], -1, (255, 255, 255), -1)
        #mask = np.zeros(thresh.shape, dtype=np.uint8)
        x, y, w, h = cv2.boundingRect(contour)
        #print(x, y, w, h)
        #cropped, text = word_search(thresh[y+3:y+h-3, x+3:x+w-3], resized_image[y+3:y+h-3, x+3:x+w-3])
        #text = get_text(resized_image[y+3:y+h-3, x+3:x+w-3])
        #print(text)
        #print(cropped.shape)
        #mask = np.zeros(resized_image.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        cropped = cv2.bitwise_and(thresh, mask)
        cropped[mask==0] = 255
        cv2.imshow('cell', cropped)
        cv2.waitKey(160)
        #cropped, text = word_search(thresh[y+3:y+h-3, x+3:x+w-3], resized_image[y+3:y+h-3, x+3:x+w-3])
        #print(text)
        #masks.append(mask)
        #cell = cv2.bitwise_and(thresh, mask)
        #cell[mask==0] = 255
        #print(get_text(resized_image[y+5:y+h-5, x+5:x+w-5], config))
        #exit()
    #cv2.imshow('invert', cropped)
    #cv2.waitKey()
