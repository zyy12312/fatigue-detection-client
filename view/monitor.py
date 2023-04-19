import sys

import webview

import service.course
import view.login
from config.data import DEBUG
import service.monitor as monitor
import service.user as user
from utils.logger import logger

monitorWindow: webview.Window


class JsAPI:
    def getCameraList(self):
        logger.info("Get Camera List...")
        camreas = monitor.getCameraList()
        cnt = 0
        ret = []
        for x in camreas:
            ret.append({
                'label': x,
                'value': cnt
            })
            cnt += 1
        return ret

    def getCameraURL(self, cameraId):
        logger.info("Get Camera URL with Camera-" + str(cameraId))
        try:
            return {
                'success': True,
                'url': monitor.startMonitoring(cameraId)
            }
        except Exception as e:
            logger.error("Open Camera Failed:" + str(e))
            return {
                'success': False,
                'message': '打开摄像头视频流失败：' + str(e)
            }

    def stopCapture(self):
        logger.info("Stop Monitoring...")
        monitor.stopMonitoring()
        return None

    def getUser(self):
        return {
            'username': user.USER.username,
            'token': user.USER.token
        }

    def logout(self):
        save = user.USER
        save.loginStatus = False
        user.saveUser(save)
        user.USER.loginStatus = False
        user.USER.token = None
        view.login.loginWindow.show()
        view.login.loginWindow.evaluate_js("location.reload()")
        monitorWindow.events.closed -= quitSystem
        monitorWindow.destroy()


def quitSystem():
    logger.info("Close Button Pressed, System Closing...")
    if view.login.loginWindow:
        view.login.loginWindow.destroy()
    sys.exit()


def getMonitorWindow(course : service.course.course):
    from __main__ import SYSTEM_PORT
    global monitorWindow
    monitorWindow = webview.create_window("监控界面",
                                          html="<script>location.href='http://127.0.0.1:{}/monitor.html'</script>".format(
                                              SYSTEM_PORT),
                                          width=800,
                                          height=800,
                                          resizable=True,
                                          js_api=JsAPI())
    monitorWindow.events.closed += quitSystem
    return monitorWindow
