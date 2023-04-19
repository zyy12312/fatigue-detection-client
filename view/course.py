import sys

import webview

from service import user
import service.user, service.course
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
        ret = service.course.getCourseList()
        if not ret:
            return None
        return ret.json()

    def getUser(self):
        return {
            'username': user.USER.username,
            'token': user.USER.token
        }

    def doStartCourse(self,course : service.course.course):
        try:
            if course is not None or course.status ==0:
                logger.info('Select Failed, selected course is None Or course is not time' % course.course_name)
                return {
                    'success': False,
                    'message': 'Course status Error'
                }
            else:
                logger.info('Select successfully, selected course is:' % course.course_name)
            # ! 跳转
                courseWindow.hide()
                view.monitor.getMonitorWindow(course)
                return {
                    'success': True,
                    'message': 'ok'
                }
        except Exception as e:
            logger.warn('Error, message: %s' % e)
            return {
                'success': False,
                'message': str(e)
            }
    def logout(self):
        save = user.USER
        save.loginStatus = False
        user.saveUser(save)
        user.USER.loginStatus = False
        user.USER.token = None
        view.login.loginWindow.show()
        view.login.loginWindow.evaluate_js("location.reload()")
        courseWindow.events.closed -= quitSystem
        courseWindow.destroy()


def quitSystem():
    logger.info("Close Button Pressed, System Closing...")
    if view.login.loginWindow:
        view.login.loginWindow.destroy()
    sys.exit()


def getCourseWindow():
    global courseWindow
    courseWindow = webview.create_window("课程列表",
                                         "templates/login.html",
                                         width=440,
                                         height=440,
                                         resizable=False,
                                         js_api=JsAPI())
    courseWindow.events.closed += quitSystem
    return courseWindow

