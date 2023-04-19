import requests

import Config
from service.user import User


class course:
    record_id : str
    course_name : str
    course_description : str
    teacher_name : str
    status : int
    def __init__(self):
        pass
def getCourseList(u : User):
    ret = requests.post(f"{Config.BASE_URL}/api/v1/records/list",
                        data=u.token).json()
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