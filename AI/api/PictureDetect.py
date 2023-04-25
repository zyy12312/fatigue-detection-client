from threading import Timer

import webview
from torch.autograd import Variable
from ..detection import *
from ..ssd_net_vgg import *
from ..voc0712 import *
import torch
import torch.nn as nn
import numpy as np
import cv2
from .. import utils
import torch.backends.cudnn as cudnn
import time

MODEL_PATH = '../weights/fatigue_detection_model.pth'

monitorWindow: webview.Window

class FatigueDetection:

    def __init__(self, model_path: str = MODEL_PATH, carry_img: bool = False):

        ##torch.device("mps")
        # 检测cuda是否可用
        if torch.cuda.is_available():
            torch.set_default_tensor_type('torch.cuda.FloatTensor')
        # 初始化网络
        self.net = SSD()
        self.net = torch.nn.DataParallel(self.net)
        self.net.train(mode=False)
        self.net.load_state_dict(torch.load(model_path, map_location=lambda storage, loc: storage))
        if torch.cuda.is_available():
            self.net = self.net.cuda()
            cudnn.benchmark = True

        self.img_mean = (104.0, 117.0, 123.0)
        # 保存检测结果的List
        # 眼睛和嘴巴都是，张开为‘1’，闭合为‘0’
        self.list_B = np.ones(15)  # 眼睛状态List,建议根据fps修改
        self.list_Y = np.zeros(50)  # 嘴巴状态list，建议根据fps修改
        self.list_Y1 = np.ones(5)  # 如果在list_Y中存在list_Y1，则判定一次打哈欠，同上，长度建议修改
        self.blink_count = 0  # 眨眼计数
        self.yawn_count = 0
        self.blink_start = time.time()  # 炸眼时间
        self.yawn_start = time.time()  # 打哈欠时间
        self.blink_freq = 0.5
        self.yawn_freq = 0
        self.carry_img = carry_img
        self.colors_tableau = [(214, 39, 40), (23, 190, 207), (188, 189, 34), (188, 34, 188), (205, 108, 8)]

    """
    @Param img: 传入的图片（单张）
    """

    def check_picture(self, img: np.ndarray):
        ret = {'error': None}
        flag_B = True  # 是否闭眼的flag
        flag_Y = False
        num_rec = 0  # 检测到的眼睛的数量
        start = time.time()  # 计时
        # 检测
        x = cv2.resize(img, (300, 300)).astype(np.float32)
        x -= self.img_mean
        x = x.astype(np.float32)
        x = x[:, :, ::-1].copy()
        x = torch.from_numpy(x).permute(2, 0, 1)
        xx = Variable(x.unsqueeze(0))
        if torch.cuda.is_available():
            xx = xx.cuda()
        y = self.net(xx)
        softmax = nn.Softmax(dim=-1)
        detect = Detect.apply
        priors = utils.default_prior_box()

        loc, conf = y
        loc = torch.cat([o.view(o.size(0), -1) for o in loc], 1)
        conf = torch.cat([o.view(o.size(0), -1) for o in conf], 1)

        detections = detect(
            loc.view(loc.size(0), -1, 4),
            softmax(conf.view(conf.size(0), -1, config.class_num)),
            torch.cat([o.view(-1, 4) for o in priors], 0),
            config.class_num,
            200,
            0.7,
            0.45
        ).data
        labels = VOC_CLASSES
        ret["res"] = []
        scale = torch.Tensor(img.shape[1::-1]).repeat(2)
        for i in range(detections.size(1)):
            j = 0
            while detections[0, i, j, 0] >= 0.4:
                score = detections[0, i, j, 0]
                #print(type(score))
                label_name = labels[i - 1]
                if label_name == 'closed_eye':
                    flag_B = False
                if label_name == 'open_mouth':
                    flag_Y = True
                ret["res"].append((label_name, score))
                display_txt = '%s:%.2f' % (label_name, score)
                pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
                color = self.colors_tableau[i]
                #print((float)(pt[0]))
                cv2.rectangle(img, (((int)(pt[0])),((int)(pt[1]))), (((int)(pt[2])),((int)(pt[3]))), color, 2)
                cv2.putText(img, display_txt, (int(pt[0]), int(pt[1]) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (255, 255, 255),
                            1, 8)
                j += 1
                num_rec += 1
        if num_rec > 0:
            if flag_B:
                # print(' 1:eye-open')
                self.list_B = np.append(self.list_B, 1)  # 睁眼为‘1’
            else:
                # print(' 0:eye-closed')
                self.list_B = np.append(self.list_B, 0)  # 闭眼为‘0’
            self.list_B = np.delete(self.list_B, 0)
            if flag_Y:
                self.list_Y = np.append(self.list_Y, 1)
            else:
                self.list_Y = np.append(self.list_Y, 0)
            self.list_Y = np.delete(self.list_Y, 0)
        else:
            ret = {'error': {'code': 10, 'message': 'people leave'}, "time": time.time()}
            if self.carry_img:
                return ret, img
            else:
                return ret
        # print(list)
        # 实时计算PERCLOS
        perclos = 1 - np.average(self.list_B)
        ret["perclos"] = perclos
        if self.list_B[13] == 1 and self.list_B[14] == 0:
            # 如果上一帧为’1‘，此帧为’0‘则判定为眨眼
            ret["message"] = "眨眼"
            self.blink_count += 1
        blink_T = time.time() - self.blink_start
        if blink_T > 10:
            # 每10秒计算一次眨眼频率
            blink_freq = self.blink_count / blink_T
            self.blink_start = time.time()
            self.blink_count = 0
            ret["blink_freq"] = blink_freq
        # 检测打哈欠
        # if Yawn(list_Y,list_Y1):
        if (self.list_Y[len(self.list_Y) - len(self.list_Y1):] == self.list_Y1).all():
            ret["message"] = "打哈欠"
            self.yawn_count += 1
            self.list_Y = np.zeros(50)
        # 计算打哈欠频率
        yawn_T = time.time() - self.yawn_start
        if yawn_T > 60:
            yawn_freq = self.yawn_count / yawn_T
            self.yawn_start = time.time()
            self.yawn_count = 0
            ret["yawn_freq"] = yawn_freq
        ret["is_tired"] = False
        # 此处为判断疲劳部分
        if perclos > 0.4:
            ret["is_tired"] = True
        elif self.blink_freq < 0.25:
            ret["is_tired"] = True
            self.blink_freq = 0.5  # 如果因为眨眼频率判断疲劳，则初始化眨眼频率
        elif self.yawn_freq > 5.0 / 60:
            ret["is_tired"] = True
            self.yawn_freq = 0  # 初始化，同上
        ret["time"] = time.time()

        if self.carry_img:
            return ret, img
        return ret

def showResult(self):
    ret, img = cap.read()  # 读取图片
    cv2.imshow("ssd", img)
    print(derector.check_picture(img), flush=True)
    if cv2.waitKey(100) & 0xff == ord('q'):
        cap.release()
        cv2.destroyAllWindows()

##def generateNetPackage(self):

if __name__ == "__main__":
    derector = FatigueDetection(MODEL_PATH)
    cap = cv2.VideoCapture(0)
    while True:
        ###showResult()
        Timer(0.4, showResult(), ()).start()
        ###time.sleep(0.4)
        if False:
            break
    cap.release()
    cv2.destroyAllWindows()
