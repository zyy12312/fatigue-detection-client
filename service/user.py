import pickle

import Config
from utils.logger import logger
from config.data import USER_PATH
import requests


class User:
    username: str
    password: str
    token: str
    loginStatus: bool
    expire: int

    def __init__(self):
        pass


def userLogin(u: User):
    if Config.DEBUG:
        if u.username == 'admin' and u.password == '123456':
            u.token = 'token'
            u.loginStatus = True
            u.expire = time.time() + 3600 * 12
        else:
            raise Exception("用户名或密码错误")
    else:
        ret = requests.post(f"{Config.BASE_URL}/api/v1/users/login",
                            data={"username": u.username, "password": u.password}).json()
        if ret["code"] == 200:
            u.token = ret["data"]["token"]
            u.loginStatus = True
            u.expire = ret["data"]["expire"] // 1000
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


updateToken = userLogin
USER = User()
