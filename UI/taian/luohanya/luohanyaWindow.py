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
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget, QPushButton, QLabel,QComboBox, QLineEdit, QGridLayout, QDesktopWidget, QHBoxLayout, QProgressBar, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QFont
from UI.taian.guoyuefu.taWidget import *
from UI.taian.luohanya.lhyWidget import *
from UI.taian.taohuayu.thyWidget import *
from UI.taian.tianwaicun.twcWidget import *

class LuohanyaWindow(QWidget):
    def __init__(self):
        super().__init__() # 初始化
        self.initUI()  # 初始化界面
        """罗汉崖相关全局变量"""
        self.lhy_positionList = []
        self.lhy_savePath = "detectDir/luohanya/capImg/"
        #创建抓图保存文件夹
        self.mkdir(self.lhy_savePath)

    def initUI(self):

        self.scanTab = QWidget()
        self.recTab = QWidget()
        self.histTab = QWidget()

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.scanTab,"林区扫描")
        #self.tabWidget.addTab(self.recTab,"位置复现")
        #self.tabWidget.addTab(self.histTab,"历史记录")
        self.tabWidget.currentChanged['int'].connect(self.tabFun)
        self.tabWidget.setFixedSize(700,590)
        # 设置样式
        self.tabWidget.setStyleSheet('QTabWidget::pane{border: 1px solid white; top: -1px;background: transparent;}QTabBar::tab{background-color:rgba(143,153,159,0.5);color:white}QTabBar::tab:selected{background-color:#B5BDBD}')
        
        #----------------#
        #    监控窗口
        #----------------#
        # topWidget
        self.scan_imageLabel = QLabel('松材线虫病害除治系统\n罗汉崖')
        self.scan_imageLabel.setWordWrap(True)
        self.scan_imageLabel.setAlignment(Qt.AlignCenter)#字体居中
        self.scan_imageLabel.setStyleSheet("color:white")#字体颜色
        self.scan_imageLabel.setFont(QFont("Microsoft YaHei",30,QFont.Bold))#设置字体  Roman times
        self.scan_imageLabel.setFixedSize(640,370)
        self.scan_imageLabel.setScaledContents (True)

        # 进度条
        # self.scan_prgBar = QProgressBar(self)
        # self.scan_prgBar.setMaximumWidth(640)

        self.scan_topWidget = QWidget()
        self.scan_topLayout = QGridLayout()
        self.scan_topLayout.addWidget(self.scan_imageLabel,0,0)
        #self.scan_topLayout.addWidget(self.scan_prgBar,1,0)
        self.scan_topWidget.setLayout(self.scan_topLayout)
        # topWidget 大小
        self.scan_topWidget.setFixedSize(670,420)
        self.scan_topWidget.setStyleSheet("background-color:rgba(143,153,159,0.5)")

        #bottomWidget
        # 开始按钮
        self.scan_startBtn = QPushButton('查询')
        self.scan_startBtn.clicked.connect(self.startBtnSlot)
        self.scan_startBtn.setStyleSheet("background-color:orange;border-radius:3px;color:white")
        self.scan_startBtn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
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
        self.scan_bottomWidget.setStyleSheet("background-color:rgba(143,153,159,0.5)")
        self.scan_bottomWidget.setFixedSize(670,60)

        # scanWidget面布局
        #scanWidget
        self.scanLayout = QGridLayout()
        self.scanLayout.addWidget(self.scan_topWidget, 0, 0)
        #self.scanLayout.addWidget(self.scan_middleWidget, 1, 0)
        self.scanLayout.addWidget(self.scan_startBtn, 2, 0)
       #self.scanLayout.addWidget(self.scan_prgBar, 3, 0)
        self.scanLayout.setSpacing(0)

        self.scanTab.setLayout(self.scanLayout)
        
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)

     # 开始按钮响应函数
    def startBtnSlot(self):
        # 更改Label提示
        self.scan_imageLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # 设置字体  Roman times
        self.scan_imageLabel.setText('准备中，请等待...')
        # 开始截图
        self.captrueImgThread = LuohanyaCaptureThread(self.lhy_positionList)
        #self.twc_captrueImgThread.startCaptureSig.connect(self.twc_prgBar.setMaximum)
        # 展示抓取到的图片
        self.captrueImgThread.getImageSig.connect(self.displyImage)

        self.captrueImgThread.start()
    #显示抓取到的图片
    def displyImage(self,imgPathstr):
        print("显示图片")
        png = QtGui.QPixmap("detectDir/luohanya/capImg/lhy.jpg")
        png.scaled(650,365)
        self.scan_imageLabel.setPixmap(png)


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
            #self.openHistDir() # 打开历史记录文件夹
        else :
            print(index)
