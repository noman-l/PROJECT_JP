import cv2
import numpy as np

img = cv2.imread('img.png')

h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5, 5), 0)

canny = None


def nothing(x):
    update_canny()
    pass


def update_canny():
    global canny
    threshold1 = cv2.getTrackbarPos('Threshold1', 'Canny')
    threshold2 = cv2.getTrackbarPos('Threshold2', 'Canny')
    canny = cv2.Canny(blur, threshold1, threshold2)
    cv2.imshow('Canny', canny)
    update_result()


def update_result():
    global canny
    global img
    points = np.array([[[1, 472], [11, 297], [270, 239], [461, 207], [513, 201], [911, 605]]], dtype=np.int32)
    black_color = (0, 0, 0)
    img_with_polyline = cv2.polylines(canny, [points], False, black_color, 2)
    cv2.imshow('m', img_with_polyline)
    # Mask 생성
    mask = np.zeros_like(canny)

    cv2.fillPoly(mask, [points], (255))

    res_and = cv2.bitwise_and(canny, img_with_polyline, mask=mask)
    cv2.imshow('z', res_and)

    lines = cv2.HoughLinesP(res_and, 1, np.pi / 180, threshold=40, minLineLength=50, maxLineGap=50)
    result = np.zeros_like(img)  # 빈 이미지 생성
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)

    final_result = cv2.addWeighted(img, 0.8, result, 1, 0)
    cv2.imshow('Result', final_result)


cv2.namedWindow('Canny')
cv2.createTrackbar('Threshold1', 'Canny', 100, 500, nothing)
cv2.createTrackbar('Threshold2', 'Canny', 200, 500, nothing)
cv2.setTrackbarPos('Threshold1', 'Canny', 100)
cv2.setTrackbarPos('Threshold2', 'Canny', 200)

update_canny()

cv2.waitKey(0)
cv2.destroyAllWindows()
