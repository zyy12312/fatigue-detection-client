import ctypes
import inspect

from utils.logger import logger


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        logger.error("Failed to send message: invalid thread id")
        return False
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        logger.error("PyThreadState_SetAsyncExc Failed: System Error.")
        return False
    logger.info("Message Sent.")
    return True


def stop_thread(thread):
    logger.info("Stopping Thread-" + str(thread.ident))
    if _async_raise(thread.ident, SystemExit):
        logger.info("Thread-%s Stopped." % thread.ident)
    else:
        logger.error("Thread-%s Stop Failed." % thread.ident)
