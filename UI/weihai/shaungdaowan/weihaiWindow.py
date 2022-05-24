import os
from PIL import Image
# from yolo import YOLO
import argparse
import threading
from sys import platform
import sys, requests, json, time, base64, os, logging
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import QUrl, QByteArray, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget, QPushButton, QLabel,QComboBox, QLineEdit, QGridLayout, QDesktopWidget, QHBoxLayout, QProgressBar, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QFont
from UI.weihai.shaungdaowan.whWidget import *


class WeihaiWindow(QWidget):
    def __init__(self):
        super().__init__() # 初始化
        with open("shuangdaowan.log", 'a+', encoding='utf8') as logFile:
            time_now = time.strftime("%Y%m%d-%H%M", time.localtime()) #获取当前时间
            print("\n\n\n\n********************************   %s   ********************************\n\n"%time_now, file=logFile)
        self.initUI()  # 初始化界面
        """威海相关全局变量"""
        self.positionList = []
        self.backgroundRole()
        self.savePath = "detectDir\\weihai\\capImg\\"
        #云台扫描范围
        self.setRangeOfCamera()
        self.mkdir(self.savePath)
        self.updateDisplyStartUploadSlot(100)
        self.scan_prgBar.setValue(10)
        # self.test_detecting()
        # self.test_repeat()
        # self.test_connectMonitor()
        # self.test_scan()

    def initUI(self):

        self.scanTab = QWidget()
        self.recTab = QWidget()
        self.histTab = QWidget()

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.scanTab,"林区扫描")
        self.tabWidget.addTab(self.recTab,"位置复现")
        self.tabWidget.addTab(self.histTab,"历史记录")
        self.tabWidget.currentChanged['int'].connect(self.tabFun)
        self.tabWidget.setFixedSize(700,590)
        #----------------#
        #    扫山窗口
        #----------------#
        # topWidget
        self.scan_imageLabel = QLabel('智能松材线虫病树监测系统\n双岛湾')
        self.scan_imageLabel.setWordWrap(True)
        self.scan_imageLabel.setAlignment(Qt.AlignCenter)#字体居中
        self.scan_imageLabel.setFixedSize(640,370)
        self.scan_imageLabel.setScaledContents (True)
        self.scan_imageLabel.setObjectName('scan_imageLabel')

        # 进度条
        self.scan_prgBar = QProgressBar(self, textVisible=False)
        # self.scan_prgBar = QProgressBar(self)
        self.scan_prgBar.setMaximumWidth(640)
        self.scan_prgBar.setObjectName('GreenProgressBar')

        self.scan_topWidget = QWidget()
        self.scan_topLayout = QGridLayout()
        self.scan_topLayout.addWidget(self.scan_imageLabel,0,0)
        self.scan_topLayout.addWidget(self.scan_prgBar,1,0)
        self.scan_topWidget.setLayout(self.scan_topLayout)
        # topWidget 大小
        self.scan_topWidget.setFixedSize(670,420)
        self.scan_topWidget.setObjectName('scan_topWidget')

        #middleWidget
        self.scan_panLabel = QLabel('水平值')
        self.scan_panLabel.setFixedSize(60,28)
        self.scan_panLabel.setAlignment(Qt.AlignRight)

        self.scan_panLineEdit = QLineEdit('0')
        self.scan_panLineEdit.setFocusPolicy(Qt.NoFocus)
        self.scan_panLineEdit.setObjectName('scan_panLineEdit')

        self.scan_tiltLabel = QLabel('俯仰值')
        self.scan_tiltLabel.setFixedSize(60,28)
        self.scan_tiltLabel.setAlignment(Qt.AlignRight)#文字居右对齐

        self.scan_tiltLineEdit = QLineEdit('0')
        self.scan_tiltLineEdit.setFocusPolicy(Qt.NoFocus)
        self.scan_tiltLineEdit.setObjectName('scan_tiltLineEdit')

        self.scan_zoomLabel = QLabel('变焦值')
        self.scan_zoomLabel.setFixedSize(60,28)
        self.scan_zoomLabel.setAlignment(Qt.AlignRight)

        self.scan_zoomLineEdit = QLineEdit('0')
        self.scan_zoomLineEdit.setFocusPolicy(Qt.NoFocus)
        self.scan_zoomLineEdit.setObjectName('scan_zoomLineEdit')

        self.scan_paramLayout = QGridLayout()
        self.scan_paramLayout.addWidget(self.scan_panLabel, 0, 0)
        self.scan_paramLayout.addWidget(self.scan_panLineEdit, 0, 1)
        self.scan_paramLayout.addWidget(self.scan_tiltLabel, 0, 2)
        self.scan_paramLayout.addWidget(self.scan_tiltLineEdit, 0, 3)
        self.scan_paramLayout.addWidget(self.scan_zoomLabel, 0, 4)
        self.scan_paramLayout.addWidget(self.scan_zoomLineEdit, 0, 5)

        self.scan_paramWidget = QWidget()
        self.scan_paramWidget.setLayout(self.scan_paramLayout)
        self.scan_paramWidget.setFixedSize(500,50)
        self.scan_paramWidget.setObjectName('scan_paramWidget')

        self.scan_middleWidget = QWidget()
        self.scan_middleLayout = QGridLayout()
        self.scan_middleLayout.addWidget(self.scan_paramWidget,0,0)
        self.scan_middleWidget.setLayout(self.scan_middleLayout)
        self.scan_middleWidget.setFixedSize(670,65)
        self.scan_middleWidget.setObjectName('scan_middleWidget') 

        #bottomWidget
        # 开始按钮
        self.scan_startBtn = QPushButton('开始检测')
        self.scan_startBtn.clicked.connect(self.startBtnSlot)
        self.scan_startBtn.setFixedSize(670,35)

        
        self.scan_btnWidget = QWidget()
        self.scan_btnLayout = QGridLayout()

        self.scan_btnLayout.addWidget(self.scan_startBtn, 1,0)
        self.scan_btnWidget.setLayout(self.scan_btnLayout)
        self.scan_btnLayout.setSpacing(0)
        self.scan_btnWidget.setFixedSize(670,50)

        self.scan_bottomWidget = QWidget()
        self.scan_bottomLayout = QGridLayout()
        self.scan_bottomLayout.addWidget(self.scan_btnWidget,0,0)
        self.scan_bottomWidget.setLayout(self.scan_bottomLayout)
        self.scan_bottomLayout.setSpacing(0)
        self.scan_bottomWidget.setFixedSize(670,60)
        self.scan_bottomWidget.setObjectName('scan_bottomWidget') 

        # scanWidget面布局
        #scanWidget
        self.scanLayout = QGridLayout()
        self.scanLayout.addWidget(self.scan_topWidget, 0, 0)
        self.scanLayout.addWidget(self.scan_middleWidget, 1, 0)
        self.scanLayout.addWidget(self.scan_startBtn, 2, 0)
        self.scanLayout.setSpacing(0)

        self.scanTab.setLayout(self.scanLayout)
        
        #------------------#
        #   位置复现窗口
        #------------------#
        # topWidget
        self.rec_imageLabel = QLabel('请输入参数并点击\n查询按钮')
        self.rec_imageLabel.setWordWrap(True)
        self.rec_imageLabel.setAlignment(Qt.AlignCenter)#字体居中
        self.rec_imageLabel.setFixedSize(640,370)
        self.rec_imageLabel.setScaledContents (True)
        self.rec_imageLabel.setObjectName('rec_imageLabel') 

        self.rec_topWidget = QWidget()
        self.rec_topLayout = QGridLayout()
        self.rec_topLayout.addWidget(self.rec_imageLabel,0,0)
        self.rec_topWidget.setLayout(self.rec_topLayout)
        # topWidget 大小
        self.rec_topWidget.setFixedSize(670,420)
        self.rec_topWidget.setObjectName('rec_topWidget') 
        #middleWidget
        self.rec_panLabel = QLabel('水平值')
        self.rec_panLabel.setFixedSize(60,28)
        self.rec_panLabel.setAlignment(Qt.AlignRight)

        self.rec_panLineEdit = QLineEdit('0')

        self.rec_tiltLabel = QLabel('俯仰值')
        self.rec_tiltLabel.setFixedSize(60,28)
        self.rec_tiltLabel.setAlignment(Qt.AlignRight)#文字居右对齐

        self.rec_tiltLineEdit = QLineEdit('0')

        self.rec_zoomLabel = QLabel('变焦值')
        self.rec_zoomLabel.setFixedSize(60,28)
        self.rec_zoomLabel.setAlignment(Qt.AlignRight)

        self.rec_zoomLineEdit = QLineEdit('0')

        self.rec_paramLayout = QGridLayout()
        self.rec_paramLayout.addWidget(self.rec_panLabel, 0, 0)
        self.rec_paramLayout.addWidget(self.rec_panLineEdit, 0, 1)
        self.rec_paramLayout.addWidget(self.rec_tiltLabel, 0, 2)
        self.rec_paramLayout.addWidget(self.rec_tiltLineEdit, 0, 3)
        self.rec_paramLayout.addWidget(self.rec_zoomLabel, 0, 4)
        self.rec_paramLayout.addWidget(self.rec_zoomLineEdit, 0, 5)

        self.rec_paramWidget = QWidget()
        self.rec_paramWidget.setLayout(self.rec_paramLayout)
        self.rec_paramWidget.setFixedSize(500,50)

        self.rec_middleWidget = QWidget()
        self.rec_middleLayout = QGridLayout()
        self.rec_middleLayout.addWidget(self.rec_paramWidget,0,0)
        self.rec_middleWidget.setLayout(self.rec_middleLayout)
        self.rec_middleWidget.setFixedSize(670,65)
        self.rec_middleWidget.setObjectName('rec_middleWidget')

        #bottomWidget
        # 查询按钮
        self.rec_startBtn = QPushButton('查询')
        self.rec_startBtn.clicked.connect(self.recept)
        self.rec_startBtn.setFixedSize(670,35)
        self.rec_startBtn.setObjectName("rec_startBtn")

        
        self.rec_btnWidget = QWidget()
        self.rec_btnLayout = QGridLayout()

        self.rec_btnLayout.addWidget(self.rec_startBtn, 1,0)
        self.rec_btnWidget.setLayout(self.rec_btnLayout)
        self.rec_btnLayout.setSpacing(0)
        self.rec_btnWidget.setFixedSize(670,50)

        self.rec_bottomWidget = QWidget()
        self.rec_bottomLayout = QGridLayout()
        self.rec_bottomLayout.addWidget(self.rec_btnWidget,0,0)
        self.rec_bottomWidget.setLayout(self.rec_bottomLayout)
        self.rec_bottomLayout.setSpacing(0)
        self.rec_bottomWidget.setFixedSize(670,60)
        self.rec_bottomWidget.setObjectName('rec_bottomWidget')

        # recWidget界面布局
        #recWidget
        self.recLayout = QGridLayout()
        self.recLayout.addWidget(self.rec_topWidget, 0, 0)
        self.recLayout.addWidget(self.rec_middleWidget, 1, 0)
        self.recLayout.addWidget(self.rec_startBtn, 2, 0)
        self.recLayout.setSpacing(0)

        self.recTab.setLayout(self.recLayout)


        #------------------#
        #   历史记录窗口
        #------------------#
        # histWidget
        self.hits_topWidget = QWidget()
        self.btn1 = QPushButton("2021年8月15日")
        self.btn1.setFixedSize(142, 88)
        self.btn1.setObjectName("btn")
        self.btn2 = QPushButton("2021年9月23日")
        self.btn2.setFixedSize(142, 88)
        self.btn2.setObjectName("btn")
        self.btn3 = QPushButton("2021年10月12日")
        self.btn3.setFixedSize(142, 88)
        self.btn3.setObjectName("btn")
        self.btn4 = QPushButton("2021年10月23日")
        self.btn4.setFixedSize(142, 88)
        self.btn4.setObjectName("btn")
        self.btn5 = QPushButton("2021年11月4日")
        self.btn5.setFixedSize(142, 88)
        self.btn5.setObjectName("btn")
        self.btn6 = QPushButton("2021年11月15日")
        self.btn6.setFixedSize(142, 88)
        self.btn6.setObjectName("btn")
        self.btn7 = QPushButton("2021年11月17日")
        self.btn7.setFixedSize(142, 88)
        self.btn7.setObjectName("btn")
        self.btn8 = QPushButton("2021年12月23日")
        self.btn8.setFixedSize(142, 88)
        self.btn8.setObjectName("btn")
        self.btn9 = QPushButton("2022年1月5日")
        self.btn9.setFixedSize(142, 88)
        self.btn9.setObjectName("btn")
        self.btn10 = QPushButton("2022年1月7日")
        self.btn10.setFixedSize(142, 88)
        self.btn10.setObjectName("btn")
        self.btn11 = QPushButton("2022年1月23日")
        self.btn11.setFixedSize(142, 88)
        self.btn11.setObjectName("btn")
        self.btn12 = QPushButton("2022年2月19日")
        self.btn12.setFixedSize(142, 88)
        self.btn12.setObjectName("btn")
        self.btn13 = QPushButton("2022年2月23日")
        self.btn13.setFixedSize(142, 88)
        self.btn13.setObjectName("btn")
        self.hist_btnLayout = QGridLayout()
        self.hist_btnLayout.addWidget(self.btn1,0,0)
        self.hist_btnLayout.addWidget(self.btn2,0,1)
        self.hist_btnLayout.addWidget(self.btn3,0,2)
        self.hist_btnLayout.addWidget(self.btn4,0,3)
        self.hist_btnLayout.addWidget(self.btn5,1,0)
        self.hist_btnLayout.addWidget(self.btn6,1,1)
        self.hist_btnLayout.addWidget(self.btn7,1,2)
        self.hist_btnLayout.addWidget(self.btn8,1,3)
        self.hist_btnLayout.addWidget(self.btn9,2,0)
        self.hist_btnLayout.addWidget(self.btn10,2,1)
        self.hist_btnLayout.addWidget(self.btn11,2,2)
        self.hist_btnLayout.addWidget(self.btn12,2,3)
        self.hist_btnLayout.addWidget(self.btn13,3,0)
        self.hits_topWidget.setLayout(self.hist_btnLayout)
        # self.hits_topWidget.setFixedSize(570,60)

        self.bottomWidget = QWidget()
        self.preBtn = QLabel("<<<上一页")
        self.preBtn.setAlignment(Qt.AlignCenter)
        # self.preBtn.setStyleSheet("background-color:yellow")
        self.nextBtn = QLabel("下一页>>>")
        self.nextBtn.setAlignment(Qt.AlignCenter)
        # self.nextBtn.setStyleSheet("background-color:blue")
        self.bottomLayout = QGridLayout()
        self.bottomLayout.addWidget(self.preBtn,0,0)
        self.bottomLayout.addWidget(self.nextBtn,0,1)
        self.bottomLayout.setSpacing(0)
        self.bottomWidget.setLayout(self.bottomLayout)
        # self.bottomWidget.setStyleSheet("background-color:red")
        self.bottomWidget.setFixedSize(650,65)


        self.hist_mainLayout = QGridLayout()
        self.hist_mainLayout.addWidget(self.hits_topWidget,0, 0)
        self.hist_mainLayout.addWidget(self.bottomWidget,1, 0)
        self.hist_histWidget = QWidget()
        self.hist_histWidget.setLayout(self.hist_mainLayout)
        self.hist_histWidget.setObjectName('hist_histWidget')

        # histWidget界面布局
        #histWidget
        self.histLayout = QGridLayout()
        self.histLayout.addWidget(self.hist_histWidget, 0, 0)
        # self.histLayout.addWidget(self.hist_topWidget, 0, 0)
        # self.histLayout.addWidget(self.hist_middleWidget, 1, 0)
        # self.histLayout.addWidget(self.hist_startBtn, 2, 0)
        self.histLayout.setSpacing(0)

        self.histTab.setLayout(self.histLayout)





        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)

        with open('UI\\source.qss') as f:
            qss = f.read()
            print("weihai qss:%s"%qss)
            self.setStyleSheet(qss)

    #设置云台扫描范围
    def setRangeOfCamera(self):
        print("威海-双岛湾-扫面范围:")
        '''********************** zoom ：410 ***********************'''
        for i in range(3461,3601,12):
            for n in range(2,15,6):
                tmpStr = str(i) + '-' + str(n) + '-' + "410"
                self.positionList.append(tmpStr)
        for i in range(1,1832,12):
            for n in range(2,15,6):
                tmpStr = str(i) + '-' + str(n) + '-' + "410"
                self.positionList.append(tmpStr)    
        '''********************** zoom ：300 ***********************'''   
        for i in range(3377,3601,13):
            for n in range(20,33,6):
                tmpStr = str(i) + '-' + str(n) + '-' + "300"
                self.positionList.append(tmpStr)
        for i in range(0,2016,13):
            for n in range(20,33,6):
                tmpStr = str(i) + '-' + str(n) + '-' + "300"
                self.positionList.append(tmpStr)
        '''********************** zoom ：210 ***********************''' 
        for i in range(3348,3601,17):
            for n in range(38,46,8):
                tmpStr = str(i) + '-' + str(n) + '-' + "210"
                self.positionList.append(tmpStr)
        for i in range(0,2068,17):
            for n in range(38,46,8):
                tmpStr = str(i) + '-' + str(n) + '-' + "210"
                self.positionList.append(tmpStr)
        '''********************** zoom 150 ***********************''' 
        for i in range(3325,3601,26):
            for n in range(54,68,13):
                tmpStr = str(i) + '-' + str(n) + '-' + "150"
                self.positionList.append(tmpStr)
        for i in range(0,2092,26):
            for n in range(54,68,13):
                tmpStr = str(i) + '-' + str(n) + '-' + "150"
                self.positionList.append(tmpStr)
        '''********************** zoom 110 ***********************''' 
        for i in range(3299,3601,32):
                tmpStr = str(i) + '-' + "80" + '-' + "110"
                self.positionList.append(tmpStr)
        for i in range(0,2092,32):
                tmpStr = str(i) + '-' + "80" + '-' + "110"
                self.positionList.append(tmpStr)
        '''********************** zoom 90 ***********************''' 
        for i in range(3294,3601,38):
                tmpStr = str(i) + '-' + "96" + '-' + "90"
                self.positionList.append(tmpStr)
        for i in range(0,1960,38):
                tmpStr = str(i) + '-' + "96" + '-' + "90"
                self.positionList.append(tmpStr)
        '''********************** zoom 70 ***********************''' 
        for i in range(3294,3601,49):
                tmpStr = str(i) + '-' + "115" + '-' + "70"
                self.positionList.append(tmpStr)
        for i in range(0,1960,49):
                tmpStr = str(i) + '-' + "115" + '-' + "70"
                self.positionList.append(tmpStr)
        '''********************** zoom 60 ***********************''' 
        for i in range(3294,3601,58):
                tmpStr = str(i) + '-' + "139" + '-' + "60"
                self.positionList.append(tmpStr)
        for i in range(0,1960,58):
                tmpStr = str(i) + '-' + "139" + '-' + "60"
                self.positionList.append(tmpStr)
        '''********************** zoom 50 ***********************''' 
        for i in range(3294,3601,67):
                tmpStr = str(i) + '-' + "168" + '-' + "50"
                self.positionList.append(tmpStr)
        for i in range(0,2070,67):
                tmpStr = str(i) + '-' + "168" + '-' + "50"
                self.positionList.append(tmpStr)
        '''********************** zoom 40 ***********************''' 
        for i in range(3121,3601,90):
                tmpStr = str(i) + '-' + "201" + '-' + "40"
                self.positionList.append(tmpStr)
        for i in range(0,2070,90):
                tmpStr = str(i) + '-' + "201" + '-' + "40"
                self.positionList.append(tmpStr)
        '''********************** zoom 35 ***********************''' 
        for i in range(3121,3601,101):
                tmpStr = str(i) + '-' + "246" + '-' + "35"
                self.positionList.append(tmpStr)
        for i in range(0,2070,101):
                tmpStr = str(i) + '-' + "246" + '-' + "35"
                self.positionList.append(tmpStr)
        '''********************** zoom 27 ***********************''' 
        for i in range(3121,3601,139):
                tmpStr = str(i) + '-' + "296" + '-' + "27"
                self.positionList.append(tmpStr)
        for i in range(0,2093,139):
                tmpStr = str(i) + '-' + "296" + '-' + "27"
                self.positionList.append(tmpStr)
        '''********************** zoom 18 ***********************''' 
        for i in range(3185,3601,187):
                tmpStr = str(i) + '-' + "365" + '-' + "18"
                self.positionList.append(tmpStr)
        for i in range(0,2093,187):
                tmpStr = str(i) + '-' + "365" + '-' + "18"
                self.positionList.append(tmpStr)
        '''********************** zoom 10 ***********************''' 
        for i in range(3294,3601,313):
                tmpStr = str(i) + '-' + "458" + '-' + "10"
                self.positionList.append(tmpStr)
        for i in range(0,2093,313):
                tmpStr = str(i) + '-' + "458" + '-' + "10"
                self.positionList.append(tmpStr)
        print(self.positionList)
        #设置进度条最大值
        self.scan_prgBar.setMaximum(len(self.positionList)-1)

    # 开始按钮响应函数
    def startBtnSlot(self):
        # 设置按钮不可用
        self.scan_startBtn.setEnabled(False)
        self.scan_startBtn.setStyleSheet("background-color:#E1E1E1")
        # 更改Label提示
        self.scan_imageLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # 设置字体  Roman times
        self.scan_imageLabel.setText('准备中，请等待...')
        # 开始截图
        self.captrueImgThread = WeiHaiCaptureThread(self.positionList)
        self.captrueImgThread.startCaptureSig.connect(self.scan_prgBar.setMaximum)
        # 展示抓取到的图片
        self.captrueImgThread.getImageSig.connect(self.displyImage)
        # 更新进度条
        self.captrueImgThread.setPrgBarValSig.connect(self.setPrgBarValSlot)
        # 更新PTZ lineEdit
        self.captrueImgThread.updatePTZlineEdtSig.connect(self.setParamLineEdt)
        # 检测
        self.predictThread = WeiHaiPredictThread()
        # 开始检测
        self.captrueImgThread.captureImgFinishSig.connect(self.predictThread.start)
        # 开始检测后更新界面显示信息
        self.predictThread.startPredictSig.connect(self.updateDisplyStartPredictSlot)
		# 展示检测结果
        self.predictThread.curPreFinshiSig.connect(self.updateDisplyPredictImgSlot)
        # 更新进度条
        self.predictThread.setPrgBarValSig.connect(self.setPrgBarValSlot)
        # 检测完毕后更新界面显示
        self.predictThread.predictFinishSig.connect(self.updateDisplyPredictFinishSlot)

        self.captrueImgThread.start()

    #设置pan，tilt，zoom
    def setParamLineEdt(self,camPosStr):
        paramList = camPosStr.split("-")
        pan = paramList[0]
        tilt = paramList[1]
        zoom = paramList[2]
        self.scan_panLineEdit.setText(pan)
        self.scan_tiltLineEdit.setText(tilt)
        self.scan_zoomLineEdit.setText(zoom)


    # 更新进度条
    def setPrgBarValSlot(self, value):
        self.scan_prgBar.setValue(value)

    #开始检测，更新界面信息
    def updateDisplyStartPredictSlot(self,value):        
        # lineedit清空
        self.scan_panLineEdit.setText("")
        self.scan_tiltLineEdit.setText("")
        self.scan_zoomLineEdit.setText("")
        # 设置进度条最大值
        self.scan_prgBar.setMaximum(value)
        png = QtGui.QPixmap("")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)
        # 修改QLabel
        self.scan_imageLabel.setText('开始检测...')
	#开始检测，更新界面图片
    def updateDisplyPredictImgSlot(self,dspImgPath):
        png = QtGui.QPixmap(dspImgPath)
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)
    #检测完毕，更新界面信息
    def updateDisplyPredictFinishSlot(self,predictResSavePath):
        png = QtGui.QPixmap("")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)
        # 修改QLabel
        self.scan_imageLabel.setText('即将上传结果到服务器...')
        self.startUploadSlot(predictResSavePath)
    def startUploadSlot(self,predictResSavePath):
        # 上传
        self.uploadThread = WeiHaiUploadThread(predictResSavePath)
        # 开始上传
        self.uploadThread.start()
        self.uploadThread.startUploadSig.connect(self.updateDisplyStartUploadSlot)
        self.uploadThread.setPrgBarValSig.connect(self.setPrgBarValSlot)
        # 上传，完毕后更新界面显示
        self.uploadThread.uploadFinishSig.connect(self.updateDisplyUploadFinishSlot)

    def updateDisplyStartUploadSlot(self,value):
        self.scan_prgBar.setMaximum(value)
        png = QtGui.QPixmap("")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)
        # 修改QLabel
        self.scan_imageLabel.setText('上传检测结果到服务器...')
    

    #上传完毕后更新界面信息
    def updateDisplyUploadFinishSlot(self,save_path):
        openFolderStr = "start explorer " + save_path
        os.system(openFolderStr)
        print("openFolderStr:%s"%openFolderStr)
        # 修改QLabel
        self.scan_imageLabel.setText('上传至服务器完成!')   
        # 按钮可用
        self.scan_startBtn.setEnabled(True)
        self.scan_startBtn.setStyleSheet("background-color:orange") 

    
    #显示抓取到的图片
    def displyImage(self,imgPathstr):
        png = QtGui.QPixmap(imgPathstr)
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)

    #打开威海检测历史记录
    def openHistDir(self):
        print("历史记录")
        current_path = os.getcwd()
        openFolderStr = "start explorer " + current_path + "\\detectDir\\weihai\\detect"
        os.system(openFolderStr)
    
    #重现画面
    def displyReceptImage(self,imgPathstr):
        png = QtGui.QPixmap(imgPathstr)
        png.scaled(650,365)
        self.rec_imageLabel.setPixmap(png)
        
    #画面复现
    def recept(self):
        positionList = []
        #获取pan，tilt，zoom
        pan = self.rec_panLineEdit.text()
        tilt = self.rec_tiltLineEdit.text()
        zoom = self.rec_zoomLineEdit.text()
        posiStr = pan+"-"+tilt+"-"+zoom
        positionList.append(posiStr)
        print("画面复现positionList:",positionList)
        # 更改Label提示
        self.rec_imageLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # 设置字体  Roman times
        self.rec_imageLabel.setText('准备中，请等待...')
        # 开始截图
        self.receptImgThread = WeiHaiCaptureThread(positionList)
        # 展示抓取到的图片
        self.receptImgThread.getImageSig.connect(self.displyReceptImage)

        self.receptImgThread.start()

    # 保存抓取到的图片
    def saveCapImg(self, imgdata, imgNamStr):

        #print(len(self.positionList))
        self.mkdir("capture\\weihai")
        savePath = "capture\\weihai\\"
        time_now = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        curImgSavePath = savePath + imgNamStr + "_" +  time_now  +".jpg"
        file = open(curImgSavePath, 'wb')
        file.write(imgdata)
        file.close()

        return curImgSavePath

    #创建文件夹
    def mkdir(self, path):
        # 去除首位
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
            print(path + ' 创建成功')
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print(path + ' 目录已存在')
            return False

    def tabFun(self, index):
        if index == 2:
            print("clicked tab3")
            self.openHistDir() # 打开历史记录文件夹
        else :
            print(index)

    def test_detecting(self):
        self.scan_prgBar.setMaximum(100)
        self.scan_prgBar.setValue(55)
        png = QtGui.QPixmap("detectDir\\weihai\\detect\\1027#20#300.jpg")
        # png = QtGui.QPixmap("detectDir\\weihai\\capImg\\0#458#10.jpg")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)

        self.scan_panLineEdit.setText("1196")
        self.scan_tiltLineEdit.setText("554")
        self.scan_zoomLineEdit.setText("190")
        # 修改QLabel
        self.scan_startBtn.setEnabled(False)
        self.scan_startBtn.setStyleSheet("background-color:#E1E1E1")
        self.scan_startBtn.setText("正在检测")


    def test_repeat(self):
        # self.rec_prgBar.setMaximum(100)
        # self.rec_prgBar.setValue(55)
        png = QtGui.QPixmap("G:\\ScanForestProgram\\detectDir\\weihai\\capImg\\193#2#410.jpg")
        png.scaled(650,365)
        self.rec_imageLabel.setPixmap(png)

        self.rec_panLineEdit.setText("193")
        self.rec_tiltLineEdit.setText("2")
        self.rec_zoomLineEdit.setText("410")
        # 修改QLabel
        self.rec_startBtn.setEnabled(False)
        # self.rec_startBtn.setStyleSheet("background-color:#E1E1E1")
        # self.rec_startBtn.setText("正在检测")

    def test_connectMonitor(self):
        png = QtGui.QPixmap("")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)
        # 修改QLabel
        self.scan_imageLabel.setText('云台连接成功...')
        # 修改QLabel
        self.scan_startBtn.setEnabled(False)
        self.scan_startBtn.setStyleSheet("background-color:#E1E1E1")
        self.scan_startBtn.setText("正在检测")
    def test_scan(self):
        png = QtGui.QPixmap("")
        png.scaled(650,365)
        self.scan_prgBar.setMaximum(100)
        self.scan_prgBar.setValue(30)
        self.scan_imageLabel.setPixmap(png)
        # 修改QLabel
        self.scan_imageLabel.setText('正在扫描...')
        # 修改QLabel
        self.scan_startBtn.setEnabled(False)
        self.scan_startBtn.setStyleSheet("background-color:#E1E1E1")
        self.scan_startBtn.setText("正在检测")


