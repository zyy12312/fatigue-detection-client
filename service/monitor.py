import os
import threading

from utils.StateCounter import StateCounter
from utils.logger import logger
import cv2
from utils.network import getFreePort
from utils.thread import stop_thread
import pygame.camera
from AI.api.PictureDetect import FatigueDetection

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "true"
CAPTURE_THREAD: threading.Thread = None


def getCameraList():
    pygame.camera.init(backend=None)
    camera_id_list = pygame.camera.list_cameras()
    logger.info("Got Camera List:" + str(camera_id_list))
    return camera_id_list


class VideoCamera(object):
    def __init__(self, camera,record_id):
        self.fatigue_detection = FatigueDetection(carry_img=True, model_path="./weights/ssd_voc_5000_plus.pth")
        self.stateCounter = StateCounter(record_id)
        logger.info("Start Video Capture on Camera-" + str(camera))
        self.cap = cv2.VideoCapture(camera)

    def __del__(self):
        logger.info("Stop Video Capture")
        self.cap.release()

    def get_frame(self):
        success, image = self.cap.read()
        res, image = self.fatigue_detection.check_picture(image)
        logger.info(res)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def getFlaskThread(camera):
    def getApp():
        from flask import Flask, Response
        app = Flask("videoCapture")

        def gen():
            while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        @app.route('/')
        def video_feed():
            return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

        return app

    global CAPTURE_THREAD

    stopMonitoring()
    app = getApp()
    port = getFreePort()
    CAPTURE_THREAD = threading.Thread(target=app.run, kwargs={
        'host': '127.0.0.1',
        'port': port
    })
    CAPTURE_THREAD.start()
    logger.info("Get Flask Instance on 127.0.0.1:" + str(port))
    return port


def startMonitoring(cameraId):
    camera = VideoCamera(cameraId)
    # todo
    port = getFlaskThread(camera)
    return "http://127.0.0.1:" + str(port)


def stopMonitoring():
    global CAPTURE_THREAD
    if not CAPTURE_THREAD:
        logger.warn("No Monitor to Stop.")
        return None
    stop_thread(CAPTURE_THREAD)
    CAPTURE_THREAD = None
