import codecs
import logging
import os
import time
from logging.handlers import BaseRotatingHandler

from config.data import LOG_PREFIX

LEVEL_DICT = {
    logging.INFO: 'INFO',
    logging.WARNING: 'WARN',
    logging.ERROR: 'ERROR',
    logging.CRITICAL: 'CRITICAL',
    logging.WARN: 'WARN',
    logging.DEBUG: 'DEBUG',
    logging.FATAL: 'FATAL',
}


class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    """

    def __init__(self, filename, encoding=None, delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = "%Y-%m-%d"
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()

    def _compute_fn(self):
        return self.baseFilename + "." + time.strftime(self.suffix, time.localtime()) + ".log"

    def _open(self):
        if self.encoding is None:
            stream = open(self.currentFileName, self.mode)
        else:
            stream = codecs.open(self.currentFileName, self.mode, self.encoding)
        # simulate file name structure of `logging.TimedRotatingFileHandler`
        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError:
                pass
        try:
            os.symlink(self.currentFileName, self.baseFilename)
        except OSError:
            pass
        return stream


class Logger(logging.Logger):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, filename, name: str, when='D', back_count=3,
                 fmt=f'%(asctime)s [%(relativeCreated)d] %(levelname)6s - %(filename)s_%(funcName)s:%(lineno)d - %(message)s'):
        super().__init__(name)
        f_dir, f_name = os.path.split(filename)
        os.makedirs(f_dir, exist_ok=True)  # 当前目录新建log文件夹
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(logging.INFO)  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        sh.setLevel(logging.INFO)  # 设置屏幕上显示的日志级别
        # 多进程优化的日志处理模块
        th = MultiProcessSafeDailyRotatingFileHandler(filename=filename, when=when, backupCount=back_count,
                                                      encoding='utf-8')  # 往文件里写入指定间隔时间自动生成文件的Handler
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


logger = Logger(LOG_PREFIX, back_count=180, name="logger").logger
