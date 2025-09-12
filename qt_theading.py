from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import cv2
import face_recognition
import numpy as np

class ImageProcessingWorker(QThread):
    msg_channel = pyqtSignal(dict)
    captured = pyqtSignal(np.ndarray)
    preview_img_messaged = pyqtSignal(np.ndarray)
    # final_output = pyqtSignal(list)
    encodings_output = pyqtSignal(np.ndarray)

    is_capturing = True

    @pyqtSlot()
    def run(self):
        try:
            # captured_imgs = []
            img_encodings = []
            cam_ = cv2.VideoCapture(0)
            old_face_encd = None
            while self.is_capturing:
                ret_, frame_ = cam_.read()
                if not ret_:
                    self.msg_channel.emit({"type": "error", "msg": "Failed to get image"})
                    continue

                face_loc = face_recognition.face_locations(frame_)
                if len(face_loc):
                    self.msg_channel.emit({"type": "warn", "msg": ""})
                    face_encd = face_recognition.face_encodings(frame_, face_loc)
                    if old_face_encd is None:
                        old_face_encd = face_encd
                        continue

                    face_diff = face_recognition.face_distance(np.array(old_face_encd), np.array(face_encd))
                    if face_diff[0] == 0 or face_diff[0] > 0.6:
                        self.msg_channel.emit({"type": "warn", "msg": "⚠ Face exactly matches or not matches with previous captures."})
                        continue
                    else:
                        success_, png_ = cv2.imencode(".png", frame_)
                        if success_:
                            # captured_imgs.append(frame_)
                            for enc_ in face_encd:
                                img_encodings.append(enc_)
                            self.captured.emit(png_)

                        face_loc = face_loc[0]
                        start_ = (face_loc[3], face_loc[0])
                        end_ = (face_loc[1], face_loc[2])
                        cv2.rectangle(frame_, start_, end_, (0, 255, 0), 2)
                    old_face_encd = face_encd
                else:
                    self.msg_channel.emit({"type": "warn", "msg": "⚠ No face detected."})

                success_, png_ = cv2.imencode(".png", frame_)

                if not success_:
                    continue
                self.preview_img_messaged.emit(png_)
            # self.final_output.emit(captured_imgs)
            self.encodings_output.emit(np.array(img_encodings))
        except BaseException as e:
            print(e)

    def stop(self):
        self.is_capturing = False
