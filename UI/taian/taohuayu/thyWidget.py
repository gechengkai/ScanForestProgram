#!/usr/bin/python3

# -*- coding: utf-8 -*-


"""
ZetCode PyQt5 tutorial

This example shows an icon
in the titlebar of the window.

author: Jan Bodnar
website: zetcode.com
last edited: January 2015
"""
import os
from PIL import Image
# from yolo import YOLO
import argparse
import threading
from sys import platform
import sys, requests, json, time, base64, os
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import QUrl, QByteArray, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QDesktopWidget, QHBoxLayout, QProgressBar, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QFont
class TaohuayuCaptureThread(QThread):    
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

        #全局变量
        self.savePath = "detectDir/taohuayu/capImg/" # where are these images that were cptured to store
        self.positionList = positionList
        self.num = 0
        self.save_path = "./detectDir/taohuayu/detect/" # 
        self.curImgSavePath = "detectDir/taohuayu/capImg/"

        #连接信号与槽
        # self.workFinishSig.connect(self.startWork)

    def run(self):
        print("启动抓图线程————————————>")
        self.startWork()

    #开始抓图
    def startWork(self):
        ## 抓取
        capImgRes = self.capImgRequest() 
        if capImgRes != None:
            print(capImgRes)
            dataDic = capImgRes
            picBufDic = dataDic["picUrl"]#取出data中的pic_buf
            url = picBufDic
            print("url:")
            print(url)
            s = requests.session()
            s.keep_alive = False # 关闭多余连接
            req = s.get(url,verify=False)
            photo = QPixmap()
            photo.loadFromData(req.content)
            photo.save("detectDir/taohuayu/capImg/thy.jpg")
            self.num += 1
            #发送展示抓取图像信号
            self.getImageSig.emit("detectDir/taohuayu/capImg/thy.jpg")
        else:
            print("天外村图片抓取失败")

 

    #设置云台位置
    def capImgRequest(self):

        #组成json
        postData = dict(cameraIndexCode="003168")
        setPostionUrl = "http://112.245.48.4:8089/hey/captures"
        #print(setPostionUrl)
        setPostionResponds = requests.post(setPostionUrl, json=postData)
        print(setPostionResponds.text)
        data = json.loads(setPostionResponds.text)
        setPositionRes = data.get("data")
        print(setPositionRes)

        return setPositionRes

 