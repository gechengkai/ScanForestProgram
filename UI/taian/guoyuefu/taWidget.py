#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:    :实现了利用泰安国悦府摄像头功图像获取、图像识别、图像上传服务器三个类
@Date            :2021/09/02 11:38:21
@Author          :gechengkai
@version         :v1.0
'''
import os, sys, requests, json, time, base64, os, socket, urllib3.request, glob, argparse, threading, logging
from requests.api import head
from PIL import Image
# from yolo import YOLO
from sys import platform
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import QUrl, QByteArray, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QDesktopWidget, QHBoxLayout, QProgressBar, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QFont

from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, colorstr, non_max_suppression, \
    apply_classifier, scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path, save_one_box
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, load_classifier, time_sync

class TaianCaptureThread(QThread):    
    # 开始抓图
    startCaptureSig = QtCore.pyqtSignal(int)   
    # 一次抓图工作完成
    workFinishSig = QtCore.pyqtSignal()   
    # 成功抓取到图片
    getImageSig = QtCore.pyqtSignal(str)
    # 更新进度条信号
    setPrgBarValSig = QtCore.pyqtSignal(int)
    # 抓图完毕信号
    captureImgFinishSig = QtCore.pyqtSignal()
    # 更新ptz lineEdt 信号
    updatePTZlineEdtSig = QtCore.pyqtSignal(str)
    
    def __init__(self,positionList):
        super().__init__()
        # logger使用方法1使用，配置handler( 方法2，使用logging.basicConfig() )
        # 创建一个logger 
        self.logger = logging.getLogger("guoyuefu_capture") # 初始化logger
        self.logger.setLevel(logging.INFO) # Log 等级总开关
        # 创建一个handler，用于写入日志文件
        handler_file = logging.FileHandler(filename="guoyuefu.log", mode='a', encoding='utf-8')
        handler_file.setLevel(logging.INFO) #输出到 file 的 Log 等级
        # 创建一个handler，用来把日志写到cmd上
        handler_cmd = logging.StreamHandler()
        handler_cmd.setLevel(logging.INFO)
        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(message)s")
        handler_file.setFormatter(formatter)
        handler_cmd.setFormatter(formatter)
        # 将相应的handler添加到logger对象中
        # self.logger.addHandler(handler_cmd)
        self.logger.addHandler(handler_file)
        #全局变量
        self.savePath = "detectDir\\taian\\capImg\\" # where are these images that were cptured to store
        self.positionList = positionList # 抓取图片摄像机位置参数列表
        self.num = 0
        self.save_path = ".\\detectDir\\taian\\detect\\" # 
        self.curImgSavePath = "detectDir\\taian\\capImg\\"

    # 启动线程
    def run(self):
        self.logger.info("启动抓图线程————————————>")
        self.startWork("init")

     #开始
    def startWork(self,flag):
        if flag == "init":
            self.startCaptureSig.emit(len(self.positionList))      
            for i in range(25712,len(self.positionList)):
                self.num  = i
                self.logger.info("\n\n————————————————————————————————  %d  ————————————————————————————————"%int(self.num))
                self.logger.info("work:国悦府-第%d张图片" %(i))
                self.logger.info("work:国悦府-共%d张图片" %(len(self.positionList)))
                # 设定位置
                self.logger.info("work:1 设定云台位置")
                setPositionRes = self.setPositonRequest(self.positionList[self.num]) 
                if setPositionRes != None:
                    #延时3秒
                    time.sleep(3)
                    #截图
                    self.logger.info("work:2 截图")
                    imageBase64Str = self.cptureRequests()
                    while imageBase64Str == None:
                        self.logger.info("work:------------------------------未获取到图片,3秒后重试")
                        time.sleep(3)
                        imageBase64Str = self.cptureRequests()
                    #转成图片
                    imgdata = self.base64ToImage(imageBase64Str)
                    #保存
                    saveImagePath = self.saveCapImg(imgdata)
                    #发送展示抓取图像信号
                    self.getImageSig.emit(saveImagePath)
                    #获取相机位置
                    self.logger.info("work:3 获取云台位置")
                    camPosStr = self.getCameraPositon()
                    while camPosStr == None:
                        self.logger.info("work:------------------------------未获取到云台位置,3秒后重试")
                        time.sleep(3)
                        camPosStr = self.getCameraPositon()
                    self.updatePTZlineEdtSig.emit(camPosStr)
                    self.num += 1
                    #发射更新进度条信号
                    self.setPrgBarValSig.emit(self.num)
                else:
                    self.logger.info("work:setPosition 失败！")
                    self.logger.info("work:self.num--%s"%self.num)
                    self.startWork("retry")
                    break #跳出循环
        elif flag == "retry":
            for i in range(self.num, len(self.positionList)):
                self.logger.info("\n\n————————————————————————————————  %d  ————————————————————————————————"%int(self.num))
                self.logger.info("work:retry-国悦府-第%d张图片"%i)
                self.logger.info("work:retry-国悦府-共%d张图片"%(len(self.positionList)))
                self.num = i
                # 设定位置
                self.logger.info("work:1 设置云台位置")
                setPositionRes = self.setPositonRequest(self.positionList[self.num]) 
                if setPositionRes != None:
                    self.logger.info("work:retry-setPosition 成功！")
                    #延时3秒
                    time.sleep(3)
                    #截图
                    self.logger.info("work:retry-2 截图")
                    imageBase64Str = self.cptureRequests()
                    while imageBase64Str == None:
                        self.logger.info("work:retry-------------------------------未获取到图片,3秒后重试")
                        time.sleep(3)
                        imageBase64Str = self.cptureRequests()
                    #转成图片
                    imgdata = self.base64ToImage(imageBase64Str)
                    #保存
                    saveImagePath = self.saveCapImg(imgdata)
                    #发送展示抓取图像信号
                    self.getImageSig.emit(saveImagePath)
                    #获取相机位置
                    self.logger.info("work:retry-3 获取云台位置")
                    camPosStr = self.getCameraPositon()
                    while camPosStr == None:
                        self.logger.info("work:retry-------------------------------未获取到云台位置,3秒后重试")
                        time.sleep(3)
                        camPosStr = self.getCameraPositon()
                    self.updatePTZlineEdtSig.emit(camPosStr)
                    self.num += 1
                    #发射更新进度条信号
                    self.setPrgBarValSig.emit(self.num)
                else:
                    self.logger.info("work:retry-setPosition 失败！")
                    self.logger.info("work:retry-self.num--%d" %(self.num))
                    self.startWork("retry")
                    break #跳出循环
        self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!图片抓取完毕\n")
        self.num = 0
        #发射抓图完毕信号
        self.captureImgFinishSig.emit()

    #获取token
    def getTokenRequest(self):
        #设置超时时间 10s
        socket.setdefaulttimeout(10)
        #header 信息
        headers = {'Authorization': 'bm9uZ2RhMTpub25nZGFAMTIz'}
        #get请求
        tokenUrl = "http://218.201.180.118:9840/apiserver/v1/user/authentication-token"
        try:
            tokenResponse = requests.get(tokenUrl, headers=headers,timeout=(3,7))
        except:
            self.logger.info("------------------------------token获取失败")
            self.logger.exception(sys.exc_info())
            tokenResponse = None
        if tokenResponse == None:
           return None
        #如果token不为空
        else:
            #从返回值中获取token，保存到全局变量token中
            data = json.loads(tokenResponse.text)
            token = data.get("data")
            if token == None :
                self.logger.info("Error 获取token失败！")
                return None
            else:
                self.logger.info("获取Token成功！" + ":" + token)
                return token
        
    #设置云台位置
    def setPositonRequest(self, positionStr):
        #获取token
        token = self.getTokenRequest()
        if token != None:
            #取出水平、俯仰、放大值
            tmpList = positionStr.split("-")
            panStr = tmpList[0]
            tiltStr = tmpList[1]
            zoomStr = tmpList[2]
            self.logger.info("设置云台位置:%s-%s-%s"%(panStr,tiltStr,zoomStr))
            #组成json
            postData = dict(camera_id="37090200001311000980", pan = int(panStr), tilt=int(tiltStr), zoom=int(zoomStr))
            setPostionUrl = "http://218.201.180.118:9840/apiserver/v1//device/ptz/postion?token="+token
            try:
                setPostionResponds = requests.post(setPostionUrl, json=postData,timeout=(3,7))
            except:
                self.logger.info('设置云台位置----------------------------------设置云台位置失败')
                self.logger.exception(sys.exc_info())
                setPostionResponds = None
            if setPostionResponds != None:
                self.logger.info("设置云台位置:成功:%s"%setPostionResponds.text)
                data = json.loads(setPostionResponds.text)
                setPositionRes = data.get("data")
                return setPositionRes 
            else:
                self.logger.info('设置云台位置----------------------------------设置云台位置失败')
                return None
        else:
            self.logger.info('设置云台位置------------------------------设置云台位置时，获取token失败')
            return None
        
    #获取图像
    def cptureRequests(self):
        #设置超时时间 10s
        socket.setdefaulttimeout(10)
        token = self.getTokenRequest()# 获取token
        if token != None:
            frontStr = "http://218.201.180.118:9840/apiserver/v1//device/video/capture?token="
            backStr = "&camera_id=37090200001311000980&stream_type=0&is_local=1&data_mode=1&pic_num=1"
            cptureUrl = frontStr + token + backStr
            try:
                cptureResponse = requests.get(cptureUrl,timeout=(3,7))
            except:
                self.logger.info("获取图像:------------------------------获取图像失败")
                self.logger.exception(sys.exc_info())
                cptureResponse = None
            if cptureResponse != None:
                tmpStr1 = json.loads(cptureResponse.text)
                dataDic = tmpStr1.get("data")#取出data
                if dataDic == None:
                    self.logger.info("获取图像:dataDic_______为空:%s"%dataDic)
                    return None
                else:
                    self.logger.info("获取图像:成功:dataDic_______不为空")
                    picBufDic = dataDic[0].get("pic_buf")#取出data中的pic_buf
                    tmpStr2 = picBufDic.split(',')
                    imgStr= tmpStr2[-1]
                    return imgStr # 返回base64码
            else:
                self.logger.info('获取图像:------------------------------获取图象失败')
                return None
        else:
            self.logger.info('获取图像:------------------------------获取图象过程中，获取token失败')
            return None

    #获取云台位置
    def getCameraPositon(self):
        # 设置超时时间 10s
        socket.setdefaulttimeout(10)
        # 获取token
        token = self.getTokenRequest()
        if token != None:
            frontStr = "http://218.201.180.118:9840/apiserver/v1/device/ptz/postion?token="
            backStr = "&camera_id=37090200001311000980"
            cptureUrl = frontStr + token + backStr
            try:
                cptureResponse = requests.get(cptureUrl,timeout=(3,7))
            except:
                self.logger.info("获取云台位置:-------------------------------获取云台位置失败")
                self.logger.exception(sys.exc_info())
                cptureResponse = None
            if cptureResponse != None:
                tmpStr1 = json.loads(cptureResponse.text)
                dataDic = tmpStr1.get("data")#取出data
                if dataDic == None:
                    self.logger.info("获取云台位置:data信息为空:dataDic:%s"%dataDic)
                    tmpStr = self.positionList[self.num]
                    #取出水平、俯仰、放大值
                    tmpList = tmpStr.split("-")
                    panStr = tmpList[0]
                    tiltStr = tmpList[1]
                    zoomStr = tmpList[2]
                    camPosiStr = panStr+"-"+tiltStr+"-"+zoomStr
                    return None
                else:
                    pan = str(dataDic["pan"])#取出data中的pic_buf
                    tilt = str(dataDic["tilt"])#取出data中的pic_buf
                    zoom = str(dataDic["zoom"])#取出data中的pic_buf
                    camPosiStr = pan+"-"+tilt+"-"+zoom
                    self.logger.info("获取云台位置:成功:camPosiStr:%s"%camPosiStr)
                    return camPosiStr
            else:
                self.logger.info("获取云台位置:------------------------------获取当前云台位置失败")
                return None
        else:
            self.logger.info('获取云台位置:------------------------------获取当前云台位置过程中，获取token失败')
            return None    
        
    #base64转图片
    def base64ToImage(self,base64Str):
        imgdata = base64.b64decode(base64Str)
        return imgdata

    # 保存抓取到的图片
    def saveCapImg(self, imgdata):
        if self.num < len(self.positionList):
            panStr = self.positionList[self.num].split('-')[0]
            tiltStr = self.positionList[self.num].split('-')[1]
            zoomStr = self.positionList[self.num].split('-')[2]
            self.curImgSavePath = self.savePath + panStr +"-" + tiltStr + "-" + zoomStr +".jpg"
        file = open(self.curImgSavePath, 'wb')
        file.write(imgdata)
        file.close()

        return self.curImgSavePath

class TaianPredictThread(QThread):
    # 更新进度条
    setPrgBarValSig = QtCore.pyqtSignal(int)
    # 开始检测
    startPredictSig = QtCore.pyqtSignal(int)
    # 当前图片检测完毕
    curPreFinshiSig = QtCore.pyqtSignal(str)
    # 检测完毕
    predictFinishSig = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        # logger使用方法1使用，配置handler( 方法2，使用logging.basicConfig() )
        # 创建一个logger 
        self.logger = logging.getLogger("guoyuefu_predict") # 初始化logger
        self.logger.setLevel(logging.INFO) # Log 等级总开关
        # 创建一个handler，用于写入日志文件
        handler_file = logging.FileHandler(filename="guoyuefu.log", mode='a', encoding='utf-8')
        handler_file.setLevel(logging.INFO) #输出到 file 的 Log 等级
        # 创建一个handler，用来把日志写到cmd上
        handler_cmd = logging.StreamHandler()
        handler_cmd.setLevel(logging.INFO)
        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(message)s")
        handler_file.setFormatter(formatter)
        handler_cmd.setFormatter(formatter)
        # 将相应的handler添加到logger对象中
        # self.logger.addHandler(handler_cmd)
        self.logger.addHandler(handler_file)

        # self.sourcePaht = "E:\\DataSets\\sicktreeDataSets\\datasets-weihai-shuangdaowan\\all-images" 
        self.sourcePaht = "detectDir\\taian\\capImg" # 检测文件夹
        self.inferRestSavePath = "detectDir\\taian\\detect\\" # 检测结果保存总文件夹
        self.uploadImgPath = "" # 传递给上传类的参数，指向检测结果保存目录
        self.disPlayImgPaht = "" # 保存检测过程中要展示在界面上的图片的路径
        
    def run(self):
        self.logger.info("启动预测线程------------->")
        self.startInference()

    @torch.no_grad()
    def inference(self, weights='best.pt',  # model.pt path(s)
            source='detectDir\\taian\\capImg',  # file/dir/URL/glob, 0 for webcam
            imgsz=640,  # inference size (pixels)
            conf_thres=0.25,  # confidence threshold
            iou_thres=0.45,  # NMS IOU threshold
            max_det=1000,  # maximum detections per image
            device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
            view_img=False,  # show results
            save_txt=True,  # save results to *.txt
            save_conf=False,  # save confidences in --save-txt labels
            save_crop=False,  # save cropped prediction boxes
            nosave=False,  # do not save images/videos
            classes=None,  # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False,  # class-agnostic NMS
            augment=False,  # augmented inference
            visualize=False,  # visualize features
            update=False,  # update all models
            project='runs/detect',  # save results to project/name
            name='exp',  # save results to project/name
            exist_ok=False,  # existing project/name ok, do not increment
            line_thickness=3,  # bounding box thickness (pixels)
            hide_labels=False,  # hide labels
            hide_conf=False,  # hide confidences
            half=False,  # use FP16 half-precision inference
            ):
        save_img = not nosave and not source.endswith('.txt')  # save inference images
        webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
            ('rtsp://', 'rtmp://', 'http://', 'https://'))

        # Directories
        save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
        (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Initialize
        set_logging()
        device = select_device(device)
        half &= device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        w = weights[0] if isinstance(weights, list) else weights
        classify, suffix = False, Path(w).suffix.lower()
        pt, onnx, tflite, pb, graph_def = (suffix == x for x in ['.pt', '.onnx', '.tflite', '.pb', ''])  # backend
        stride, names = 64, [f'class{i}' for i in range(1000)]  # assign defaults
        if pt:
            model = attempt_load(weights, map_location=device)  # load FP32 model
            stride = int(model.stride.max())  # model stride
            names = model.module.names if hasattr(model, 'module') else model.names  # get class names
            if half:
                model.half()  # to FP16
            if classify:  # second-stage classifier
                modelc = load_classifier(name='resnet50', n=2)  # initialize
                modelc.load_state_dict(torch.load('resnet50.pt', map_location=device)['model']).to(device).eval()
        elif onnx:
            check_requirements(('onnx', 'onnxruntime'))
            import onnxruntime
            session = onnxruntime.InferenceSession(w, None)
        imgsz = check_img_size(imgsz, s=stride)  # check image size

        # Dataloader
        if webcam:
            view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, stride=stride)
            bs = len(dataset)  # batch_size
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride)
            bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs

        # Run inference
        if pt and device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        t0 = time.time()
        # 设置progressBar长度
        self.startPredictSig.emit(len(dataset)-1)
        self.num = 0
        for path, img, im0s, vid_cap in dataset:
            self.setPrgBarValSig.emit(self.num)
            self.num += 1
            self.logger.info("\n\n———————————  source picture path:%s  ———————————\n\n"%path)
            self.disPlayImgPaht = path
            if pt:
                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
            elif onnx:
                img = img.astype('float32')
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if len(img.shape) == 3:
                img = img[None]  # expand for batch dim

            # Inference
            t1 = time_sync()
            if pt:
                visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
                pred = model(img, augment=augment, visualize=visualize)[0]
            elif onnx:
                pred = torch.tensor(session.run([session.get_outputs()[0].name], {session.get_inputs()[0].name: img}))

            # NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
            t2 = time_sync()

            # Second-stage classifier (optional)
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)

            # Process predictions
            for i, det in enumerate(pred):  # detections per image
                if webcam:  # batch_size >= 1
                    p, s, im0, frame = path[i], f'{i}: ', im0s[i].copy(), dataset.count
                else:
                    p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)

                p = Path(p)  # to Path
                save_path = str(save_dir / p.name)  # img.jpg
                txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
                s += '%gx%g ' % img.shape[2:]  # self.logger.info string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                imc = im0.copy() if save_crop else im0  # for save_crop
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                        self.logger.info("s:%s"%s)

                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * len(line)).rstrip() % line + '\n')

                        if save_img or save_crop or view_img:  # 给图片添加标注框
                            c = int(cls)  # integer class
                            label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                            im0 = plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_width=line_thickness)
                            if save_crop:
                                save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

                # Print time (inference + NMS)
                self.logger.info(f'{s}Done. ({t2 - t1:.3f}s)')

                # Stream results
                if view_img:
                    cv2.imshow(str(p), im0)
                    cv2.waitKey(1)  # 1 millisecond

                # Save results (image with detections)
                if save_img:
                    if dataset.mode == 'image':
                        self.logger.info("\n\n—————————————  infect result save_path: %s  ———————————\n\n"%(save_path))
                        if len(det):
                            cv2.imwrite(save_path, im0)
                            self.disPlayImgPaht = save_path
                        else:
                            pass
                    else:  # 'video' or 'stream'
                        if vid_path[i] != save_path:  # new video
                            vid_path[i] = save_path
                            if isinstance(vid_writer[i], cv2.VideoWriter):
                                vid_writer[i].release()  # release previous video writer
                            if vid_cap:  # video
                                fps = vid_cap.get(cv2.CAP_PROP_FPS)
                                w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            else:  # stream
                                fps, w, h = 30, im0.shape[1], im0.shape[0]
                                save_path += '.mp4'
                            vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                        vid_writer[i].write(im0)
            # 向主进程发送信号，参数为当前要展示的图片的地址
            self.curPreFinshiSig.emit(str(self.disPlayImgPaht))
        if save_txt or save_img:
            s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
            self.logger.info(f"Results saved to {colorstr('bold', save_dir)}{s}")

        if update:
            strip_optimizer(weights)  # update model (to fix SourceChangeWarning)

        self.logger.info(f'Done. ({time.time() - t0:.3f}s)')
        # 检测完毕，向上传线程发送信号
        self.logger.info("检测完毕，向上传线程发送信号:self.uploadImgPath:%s"%self.uploadImgPath)
        self.predictFinishSig.emit(self.uploadImgPath)


    def parse_opt(self):
        time_now = time.strftime("%Y%m%d-%H%M", time.localtime()) #获取当前时间，用作时间戳, 保存文件
        self.uploadImgPath = self.inferRestSavePath+time_now+"\\" #传递给上传线程的参数，指向检测结果保存目录
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
        parser.add_argument('--source', type=str, default=self.sourcePaht, help='file/dir/URL/glob, 0 for webcam')
        parser.add_argument('--imgsz', '--img', '--img-size', type=int, default=640, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
        parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
        parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='show results')
        parser.add_argument('--save-txt', default=False, action='store_true', help='save results to *.txt')
        parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
        parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
        parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--visualize', action='store_true', help='visualize features')
        parser.add_argument('--update', action='store_true', help='update all models')
        parser.add_argument('--project', default=self.inferRestSavePath, help='save results to project/name')
        parser.add_argument('--name', default=time_now, help='save results to project/name')
        parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
        parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
        parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
        parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
        parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
        opt = parser.parse_args()
        return opt

    def startInference(self):
        opt = self.parse_opt()
        self.logger.info(colorstr('detect: ') + ', '.join(f'{k}={v}' for k, v in vars(opt).items()))
        check_requirements(exclude=('tensorboard', 'thop'))
        self.inference(**vars(opt))

class TaianUploadThread(QThread):
    # 更新进度条
    setPrgBarValSig = QtCore.pyqtSignal(int)
    # 开始上传
    startUploadSig = QtCore.pyqtSignal(int)
    # 上传完毕
    uploadFinishSig = QtCore.pyqtSignal(str)
    
    def __init__(self,resultSavePath):        
        super().__init__()
        # logger使用方法1使用，配置handler( 方法2，使用logging.basicConfig() )
        # 创建一个logger 
        self.logger = logging.getLogger("guoyuefu_upload") # 初始化logger
        self.logger.setLevel(logging.INFO) # Log 等级总开关
        # 创建一个handler，用于写入日志文件
        handler_file = logging.FileHandler(filename="guoyuefu.log", mode='a', encoding='utf-8')
        handler_file.setLevel(logging.INFO) #输出到 file 的 Log 等级
        # 创建一个handler，用来把日志写到cmd上
        handler_cmd = logging.StreamHandler()
        handler_cmd.setLevel(logging.INFO)
        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(message)s")
        handler_file.setFormatter(formatter)
        handler_cmd.setFormatter(formatter)
        # 将相应的handler添加到logger对象中
        # self.logger.addHandler(handler_cmd)
        self.logger.addHandler(handler_file)
        # 打开日志文件 
        self.resultSavePath = resultSavePath
        self.uploadList = [] # 上传图片列表
        self.uploadNum = 0 # 保存当前上传的图片编号
        
    def run(self): 
        self.logger.info("启动上传线程------------->")
        self.startUpload(self.resultSavePath)

    # 上传图片信息到服务器  此处应该与下边上传图片到服务器合为一个函数，但服务器端目前只支持分开上传，故上传图片与信息只能分开上传
    def sendMsg(self, img_name):
        socket.setdefaulttimeout(10)
        t = time.time()
        self.logger.info("treeNum:%d"%int(round(t * 1)))
        postData = dict(treeNum=str(int(round(t * 1))), workContent = "普查", img1=img_name, equipment="37090200001311000980", source="摄像头")
        # self.logger.info("postData:%s"%postData)
        postList = []
        postList.append(postData)
        self.logger.info("postList:%s"%postList)
        urlStr = "http://112.245.48.4:8083/app/upload"
        try:
            responds = requests.post(urlStr, json=postList, timeout=(3,7))
        except:
            self.logger.info('----------------------------------上传信息失败')
            self.logger.exception(sys.exc_info())
            responds = None
        if responds == None:
            return None
        else:
            tempStr = json.loads(responds.text)
            self.logger.info("tempStr.get(\"code\"):%s"%(tempStr.get("code")))
            if tempStr.get("code") == 200:
                self.logger.info("上传信息成功: %s "%(json.loads(responds.text)))
                return 200
            else:
                self.logger.info("上传信息失败: %s "%(json.loads(responds.text)))
                return None
    # 上传信息到服务器
    def sendImg(self, img_path):
        socket.setdefaulttimeout(10)
        self.logger.info("img_path:%s"%img_path)
        urlStr = "http://112.245.48.4:8083/app/file_upload"
        image = {'files': (open(img_path, 'rb'))}
        try:
            response = requests.post(urlStr, files=image, timeout=(3,7))
        except:
            self.logger.info('----------------------------------上传图片失败')
            self.logger.exception(sys.exc_info())
            response = None
        if response == None:
            return None
        else:
            tempStr = json.loads(response.text)
            self.logger.info("tempStr.get(\"code\"):%s"%(tempStr.get("code")))
            if tempStr.get("code") == 200:
                self.logger.info("上传图片成功: %s \n"%(json.loads(response.text)))
                return 200
            else:
                self.logger.info("上传图片失败: %s \n"%(json.loads(response.text)))
                return None
    # 上传图片到服务器
    def upload(self, flag):
        if flag == "init":
            for i in range(len(self.uploadList)):
                self.uploadNum = i
                self.setPrgBarValSig.emit(i+1)
                # 上传图片
                self.logger.info("init-共要上传 %d 张照片"%(len(self.uploadList)))
                self.logger.info("init-当前上传第 %d 张照片"%int(self.uploadNum+1))
                sendImgRes = self.sendImg(self.uploadList[i])
                if sendImgRes != None:
                    self.logger.info("init-第 %d 张图片上传成功！"%int(self.uploadNum+1))
                else:
                    self.logger.info("init-第 %d 张图片上传失败！"%int(self.uploadNum+1))
                    self.upload("retry") 
                    break
                # 上传信息
                self.logger.info("init-共要上传 %d 条信息"%(len(self.uploadList)))
                self.logger.info("init-当前上传第 %d 条信息"%int(self.uploadNum+1))
                tempList = self.uploadList[i].split("\\")
                img_name = tempList[-1]
                sendMsgRes = self.sendMsg(img_name)
                if sendMsgRes != None:
                    self.logger.info("init-第 %d 条信息上传成功"%int(self.uploadNum+1))
                    self.logger.info("+++第 %d 次上传完成\n\n"%int(self.uploadNum+1))
                else:
                    self.logger.info("init-第 %d 条信息上传失败！"%int(self.uploadNum+1))
                    self.upload("retry")
                    break
        elif flag == "retry":
            if self.uploadNum < 0:
                self.uploadNum = 0
            for i in range(self.uploadNum, len(self.uploadList)):
                self.uploadNum = i
                self.setPrgBarValSig.emit(int(self.uploadNum+1))
                # 上传图片
                self.logger.info("retry-共要上传%d张照片"%(len(self.uploadList)))
                self.logger.info("retry-当前上传第%d张照片"%i)
                sendImgRes = self.sendImg(self.uploadList[i])
                if sendImgRes != None:
                    self.logger.info("retry-第 %d 张图片上传成功！"%int(self.uploadNum+1))
                else:
                    self.logger.info("retry-第 %d 张图片上传失败！"%int(self.uploadNum+1))
                    self.upload("retry") 
                    break
                # 上传信息
                self.logger.info("retry-共要上传 %d 条信息"%(len(self.uploadList)))
                self.logger.info("retry-当前上传第 %d 条信息"%int(self.uploadNum+1))
                tempList = self.uploadList[i].split("\\")
                img_name = tempList[-1]
                sendMsgRes = self.sendMsg(img_name)
                if sendMsgRes != None:
                    self.logger.info("retry-第 %d 条信息上传成功"%int(self.uploadNum+1))
                    self.logger.info("+++第 %d 次上传完成\n\n"%int(self.uploadNum+1))
                else:
                    self.logger.info("retry-第 %d 条信息上传失败！"%int(self.uploadNum+1))
                    self.upload("retry")
                    break

    # 开始上传
    def startUpload(self,resultSavePath):
        RES_SAVE_PATH = resultSavePath #检测结果存放路径
        img_paths = glob.glob(os.path.join(RES_SAVE_PATH, '*.jpg')) #获取图片路径
        img_paths.sort() #排序
        self.uploadList = img_paths
        self.startUploadSig.emit(len(self.uploadList)) # 向windowWiget发送信号，设置进度条总长
        self.upload("init")
        self.logger.info("上传完毕！")
        self.uploadFinishSig.emit(resultSavePath)
