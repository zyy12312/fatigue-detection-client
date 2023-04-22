import requests

import Config
from service import user
from service.user import User


class Course:
    def __init__(self, record_id: str = None, course_name: str = None, course_description: str = None,
                 teacher_name: str = None, status: int = 0):
        self.record_id = record_id
        self.course_name = course_name
        self.course_description = course_description
        self.teacher_name = teacher_name
        self.status = status


def getCourseList():
    ret = requests.get(f"{Config.BASE_URL}/api/v1/records/list",
                       headers={
                           "Authorization": f"Bearer {user.USER.token}"
                       }).json()
    if ret["code"] == 200:
        # course_list = []
        # for i in ret["data"]["list"]:
        #     t = Course(
        #         record_id=i["_id"],
        #         course_name=i["course"]["course_name"],
        #         course_description=i["course"]["description"],
        #         teacher_name=i["teacher"]["username"],
        #         status=int(i["status"]),
        #     )
        #     course_list.append(t.__dict__)
        # u.loginStatus = True
        # u.expire = ret["data"]["expire"] // 1000
        return ret["data"]["list"]
    else:
        raise Exception("网络请求出错")
