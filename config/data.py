import os.path

BASE_DIR = './data'
LOGS_DIR = './logs'
DEBUG = False

# init Check
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)
# init Check
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

USER_PATH = os.path.join(BASE_DIR, 'user.dat')
LOG_PREFIX = os.path.join(LOGS_DIR, 'app')
