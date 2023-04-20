import threading
import time

import numpy as np
import requests

import Config


class StateCounter:
    def __init__(self, recordId: str):
        self.tired = 0
        self.leave = 0
        self.normal = 0
        # self.sum = 0
        self.record = recordId
        self.start_time = time.time() * 1000

    def countTimes(self, res):
        # print(res)
        if res['error'] is None:
            if res['is_tired']:
                self.tired += 1
            else:
                self.normal += 1
        elif res['error']['message'] is not None:
            self.leave += 1
        self.sum += 1

    def flush(self):
        s = {
            "record_id": self.record,
            "start_time": self.start_time,
            "end_time": time.time() * 1000,
            "status": int(np.argmax(np.array([self.normal, self.tired, self.leave])))
        }
        # print(s)

        threading.Thread(target=lambda: requests.post(f"{Config.BASE_URL}/api/v1/subrecords/report", json=s)).start()
        self.leave = 0
        self.normal = 0
        self.tired = 0
        self.start_time = time.time() * 1000


if __name__ == "__main__":
    s = StateCounter("123456")
    s.flush()
