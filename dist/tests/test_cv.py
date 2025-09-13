import cv2
import numpy as np
# import face_recognition_models
import face_recognition

cam_ = cv2.VideoCapture(0)
old_frame = None
old_encd = None
while True:
    ret, frame_ = cam_.read()

    if not ret:
        print("Error while capturing image")
        break

    if old_frame is None:
        old_frame = frame_
        continue

    face_loc = face_recognition.face_locations(frame_, model="hog")
    face_enc = face_recognition.face_encodings(frame_, face_loc)

    if old_encd is None:
        old_encd = face_enc
        continue

    if len(face_enc) and len(old_encd):
        print(face_recognition.face_distance(np.array(old_encd), np.array(face_enc)))

    # print(face_loc)
    # if len(face_loc):
    #
    #     face_loc = face_loc[0]
    #     # face_locations format : (y1, x2, y2, x1)
    #     start_ = (face_loc[3], face_loc[0])
    #     end_ = (face_loc[1], face_loc[2])
    #     cv2.rectangle(frame_, start_, end_, (255, 0, 0), 2)
    cv2.imshow("My Window", frame_)

    if len(face_enc):
        old_encd = face_enc

    # cv2.imshow("My Window2", old_frame)

    # face_diff = np.linalg.norm(frame_ - old_frame)
    # if face_diff > 6.0:
    #     print(face_diff)
    #     old_frame = frame_

    k = cv2.waitKey(1)
    if k%256 == 27:
        break