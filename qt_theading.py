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


class LiveFaceRecorder(QThread):
    face_img_channel = pyqtSignal(np.ndarray)
    face_encoding_channel = pyqtSignal(np.ndarray)
    msg_channel = pyqtSignal(dict)
    is_running = False
    is_paused = False

    @pyqtSlot()
    def run(self):
        try:
            self.is_running = True
            cam_ = cv2.VideoCapture(0)
            while self.is_running:
                if self.is_paused:
                    continue
                ret, frame_ = cam_.read()
                if not ret:
                    self.msg_channel.emit("Image capture failed!")
                    continue
                loc_ = face_recognition.face_locations(frame_, model="hog")
                if len(loc_):
                    face_ = face_recognition.face_encodings(frame_, loc_)
                    for item in face_:
                        self.face_encoding_channel.emit(item)

                    face_loc = loc_[0]
                    start_ = (face_loc[3], face_loc[0])
                    end_ = (face_loc[1], face_loc[2])
                    cv2.rectangle(frame_, start_, end_, (0, 255, 0), 2)
                    success_, png_ = cv2.imencode(".png", frame_)
                    if success_:
                        self.face_img_channel.emit(png_)
                else:
                    self.msg_channel.emit({"type": "warn", "msg": "No face detected!"})
        except BaseException as e:
            print(e)

    def stop(self):
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False


class UIBlockingTaskRunner(QThread):
    class TaskResp:
        _resp = None
        def __init__(self, resp_body=None):
            self._resp = resp_body

        def getResponseBody(self):
            return self._resp

        def setResponseBody(self, resp):
            self._resp = resp

    task_to_run = None
    task_response = pyqtSignal(TaskResp)
    live_progress = pyqtSignal(str)

    def __init__(self, task_to_run):
        self.task_to_run = task_to_run
        super().__init__()

    @pyqtSlot()
    def run(self):
        to_resp = self.TaskResp()
        to_resp.setResponseBody(self.task_to_run(self.emit_progress))
        self.task_response.emit(to_resp)

    def emit_progress(self, prog_):
        self.live_progress.emit(str(prog_))
