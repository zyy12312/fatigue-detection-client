import pickle

from utils.logger import logger
from config.data import USER_PATH


class User:
    username: str
    password: str
    token: str
    loginStatus: bool

    def __init__(self):
        pass


def userLogin(u: User):
    if u.username == 'admin' and u.password == '123456':
        u.token = 'token'
        u.loginStatus = True
    else:
        raise Exception("用户名或密码错误")


def saveUser(u: User):
    try:
        f = open(USER_PATH, 'wb')
        pickle.dump(u, f)
        logger.info('Saved User to file, username=' + u.username)
    except Exception as e:
        logger.error('Save User Failed, ' + str(e))


def getLoginStatus():
    global USER
    try:
        f = open(USER_PATH, 'rb')
        u = pickle.load(f)
        logger.info('Loaded User from file, username=' + u.username)
        return u
    except FileNotFoundError:
        logger.warn('Auto login information not exist.')
        return False
    except Exception as e:
        logger.warn('Auto login failed, ' + str(e))
        return False


def getToken():
    if not USER.loginStatus:
        return ''
    return USER.token


USER = User()
