import webview

import view.login
from config.data import DEBUG
from utils.logger import logger
from utils.network import getFreePort

SYSTEM_PORT = getFreePort()

if __name__ == '__main__':
    ###webview.platform = 'cocoa'
    logger.info("Program Loading.")
    view.login.getLogin()

    webview.start(debug=DEBUG, http_port=SYSTEM_PORT,http_server=True)


