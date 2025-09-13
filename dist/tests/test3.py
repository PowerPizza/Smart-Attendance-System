import cv2

img_ = cv2.imread("a.png")
print(cv2.imencode(".png", img_))
cv2.rectangle(img_, (100, 100), (300, 300), (255, 0, 0), 2)
cv2.imshow("my img", img_)
cv2.waitKey(0)