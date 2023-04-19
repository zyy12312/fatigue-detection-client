import sys

import webview

from service import user
import service.user,service.course
from utils.logger import logger
import view.monitor

courseWindow: webview.Window


class JsAPI:
    def quit(self):
        global courseWindow
        logger.info("Exit Pressed.")
        if courseWindow:
            courseWindow.destroy()
        sys.exit()

    def getCourseList(self):
        logger.info("Load Course List From HTTP Port")
        ret = service.course.getCourseList(user.USER)
        if not ret:
            return None
        return ret.json()


def quitSystem():
    logger.info("Close Button Pressed, System Closing...")
    if view.login.loginWindow:
        view.login.loginWindow.destroy()
    sys.exit()


def getCourseList():
    global courseWindow
    courseWindow = webview.create_window("课程列表",
                                         "templates/login.html",
                                         width=440,
                                         height=440,
                                         resizable=False,
                                         js_api=JsAPI())
    courseWindow.events.closed += quitSystem

    return courseWindow
