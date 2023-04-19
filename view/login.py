import sys

import webview

from service.user import User, userLogin, saveUser, getLoginStatus
import service.user
from utils.logger import logger
import view.monitor

loginWindow: webview.Window


class JsAPI:

    def quit(self):
        global loginWindow
        logger.info("Exit Pressed.")
        if loginWindow:
            loginWindow.destroy()
        sys.exit()

    def doLogin(self, username, password, remember, autoLogin):
        u = User()
        u.username = username
        u.password = password
        logger.info('Try Login, user=%s, pass=******' % username)
        save = User()
        save.username = username
        save.password = ''
        save.loginStatus = False
        try:
            if remember or autoLogin:
                save.password = password
            if autoLogin:
                save.loginStatus = True
            userLogin(u)
            service.user.USER = u
            logger.info('Logged in successfully, token=%s***' % u.token[:3])
            saveUser(save)
            # ! 跳转
            loginWindow.hide()
            view.monitor.getMonitorWindow()
            return {
                'success': True,
                'message': 'ok'
            }
        except Exception as e:
            logger.warn('Login Failed, message: %s' % e)
            saveUser(save)
            return {
                'success': False,
                'message': str(e)
            }




def getLogin():

    global loginWindow
    loginWindow = webview.create_window("登录",
                                        "templates/login.html",
                                        width=440,
                                        height=440,
                                        resizable=False,
                                        js_api=JsAPI())
    return loginWindow
