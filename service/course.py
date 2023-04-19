import requests

import Config
from service import user
from service.user import User


class course:

    def __init__(self):
        self.record_id: str
        self.course_name: str
        self.course_description: str
        self.teacher_name: str
        self.status: int

def getCourseList():
    ret = requests.post(f"{Config.BASE_URL}/api/v1/records/list",
                        data=user.USER.token).json()
    if ret["code"] == 200:
        course_list = []
        for i in ret["data"]["list"]:
            t = course()
            t.record_id = i["_id"]
            t.course_name = i["course"]["course_name"]
            t.course_description = i["course"]["description"]
            t.teacher_name = i["teacher"]["username"]
            t.status = int(i["status"])
            course_list.append(t)
        # u.loginStatus = True
        # u.expire = ret["data"]["expire"] // 1000
        return course_list
    else:
        raise Exception("网络请求出错")