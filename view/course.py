import sys

import webview

from service.user import User, userLogin, saveUser, getLoginStatus
import service.user
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
        logger.info("Load Course List From HTTP")
        #ret = getLoginStatus()
        #here need request
        if not ret:
            return None
        return {
            'username': ret.username,
            'password': ret.password,
            'login': ret.loginStatus
        }
def getCourseList():

    global courseWindow
    courseWindow = webview.create_window("课程列表",
                                        "templates/login.html",
                                        width=440,
                                        height=440,
                                        resizable=False,
                                        js_api=JsAPI())
    return courseWindow