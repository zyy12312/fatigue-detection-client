import socket

from utils.logger import logger


def getFreePort():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    ip, port = sock.getsockname()
    sock.close()
    logger.info("Got Free Port: " + str(port))
    return port
