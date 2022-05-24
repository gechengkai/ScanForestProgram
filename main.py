#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
author: gck
time  : 2021-6-26
"""
from UI.taian.guoyuefu.taianWindow import TaianWindow
from UI.taian.tianwaicun.tianwaicunWindow import TianwaicunWindow
from UI.taian.taohuayu.taohuayuWindow import TaohuayuWindow
from UI.taian.luohanya.luohanyaWindow import LuohanyaWindow
from UI.weihai.shaungdaowan.weihaiWindow import WeihaiWindow
from UI.yantai.muping.yantaiWindow import YantaiWindow
from UI.taian.guoyuefu.taWidget import *
from UI.taian.luohanya.lhyWidget import *
from UI.taian.taohuayu.thyWidget import *
from UI.taian.tianwaicun.twcWidget import *
from UI.weihai.shaungdaowan.whWidget import *
from UI.yantai.muping.ytWidget import *

import sys, requests, json, time, base64, os, logging, threading, argparse, os
from sys import platform
from lxml import etree
from PIL import Image
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import QUrl, QByteArray, QThread, qDebug, pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QApplication, QGroupBox, QToolBox, QVBoxLayout, QWidget, QPushButton, QLabel,QComboBox, QLineEdit, QGridLayout, QDesktopWidget, QHBoxLayout, QProgressBar, QStackedWidget
from PyQt5.QtGui import QFontDatabase, QPalette, QPixmap, QBrush, QFont, QIcon

logging.captureWarnings(True)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化界面
        self.initUI()
        
    #初始化界面 
    def initUI(self):

        # 泰安GroupBox
        self.taGroupBox = QGroupBox()
        
        self.gyfBtn = QPushButton("国悦府")
        self.gyfBtn.setFixedSize(120,30)
        self.thyBtn = QPushButton("桃花峪")
        self.thyBtn.setFixedSize(120,30)
        self.lhyBtn = QPushButton("罗汉崖")
        self.lhyBtn.setFixedSize(120,30)
        self.twcBtn = QPushButton("天外村")
        self.twcBtn.setFixedSize(120,30)
        # 信号与槽
        self.gyfBtn.clicked.connect(self.showBigWidget)
        self.thyBtn.clicked.connect(self.showBigWidget)
        self.lhyBtn.clicked.connect(self.showBigWidget)
        self.twcBtn.clicked.connect(self.showBigWidget)

        self.taBtnGroupLayout = QGridLayout()
        self.taBtnGroupLayout.addWidget(self.gyfBtn)
        self.taBtnGroupLayout.addWidget(self.thyBtn)
        self.taBtnGroupLayout.addWidget(self.lhyBtn)
        # self.taBtnGroupLayout.addWidget(self.twcBtn)
        self.taBtnGroupLayout.setAlignment(Qt.AlignTop)

        self.taGroupBox.setLayout(self.taBtnGroupLayout)
        self.taGroupBox.setWindowOpacity(0.80)
        self.taGroupBox.setAttribute(QtCore.Qt.WA_TranslucentBackground)
  
        # 烟台GroupBox
        self.ytGroupBox = QGroupBox()

        self.mpBtn = QPushButton("牟平")
        self.mpBtn.setFixedSize(120,30)
        self.mpBtn.clicked.connect(self.showBigWidget)

        self.ytBtnGroupLayout = QGridLayout()
        self.ytBtnGroupLayout.addWidget(self.mpBtn)
        self.ytBtnGroupLayout.setAlignment(Qt.AlignTop)

        self.ytGroupBox.setLayout(self.ytBtnGroupLayout)

        # 威海GroupBox
        self.whGroupBox = QGroupBox()

        self.sdwBtn = QPushButton("双岛湾")
        self.sdwBtn.setFixedSize(120,30)
        self.sdwBtn.clicked.connect(self.showBigWidget)

        self.whBtnGroupLayout = QGridLayout()
        self.whBtnGroupLayout.addWidget(self.sdwBtn)
        self.whBtnGroupLayout.setAlignment(Qt.AlignTop)

        self.whGroupBox.setLayout(self.whBtnGroupLayout)

        # 左侧窗口布局
        self.toolBox = QToolBox()
        self.toolBox.addItem(self.taGroupBox, "泰安")
        self.toolBox.addItem(self.whGroupBox, "威海")
        self.toolBox.addItem(self.ytGroupBox, "烟台")
        
        self.toolBox.setFixedSize(150,590)
        self.toolBox.currentChanged.connect(self.currentChangeSlot) # 点击toolbox按钮时右边部件显示对应地区内容
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.toolBox)
        self.toolBoxWiget = QWidget()
        self.toolBoxWiget.setLayout(self.vBoxLayout)
        

        
        self.taianWindow = TaianWindow()
        self.yantaiWindow = YantaiWindow()
        self.weihaiWindow =  WeihaiWindow()
        self.luohanyaWindow = LuohanyaWindow()
        self.taohuayuWindow = TaohuayuWindow()
        self.tianwaicunWindow = TianwaicunWindow()

        #stack部件
        self.stack = QStackedWidget()
        self.stack.addWidget(self.taianWindow)
        self.stack.addWidget(self.taohuayuWindow)
        self.stack.addWidget(self.luohanyaWindow)
        self.stack.addWidget(self.tianwaicunWindow)
        self.stack.addWidget(self.weihaiWindow)
        self.stack.addWidget(self.yantaiWindow)
        self.stack.setCurrentIndex(0)
        #self.stack.show()

        # mainWidget
        self.mainWidget= QWidget()
        self.mainLayout = QGridLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.toolBoxWiget,0,0)
        self.mainLayout.addWidget(self.stack,0,1)
        self.mainWidget.setLayout(self.mainLayout)
        self.mainWidget.setFixedSize(960, 650)
        
        #设置主界面背景图
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("UI\\picture\\Royal.jpg")))
        self.mainWidget.setPalette(palette)
        self.mainWidget.setWindowIcon(QIcon("UI\\picture\\icon.png"))
        self.mainWidget.setWindowTitle("智能松材线虫病树监控系统")
        
        with open('source.qss') as f:
            qss = f.read()
            print("main qss:%s"%qss)
            self.mainWidget.setStyleSheet(qss)
        self.mainWidget.show()

    def currentChangeSlot(self, index):
        print(index)
        if index == 0: # 点击“泰安”按钮时显示“国悦府”
            self.stack.setCurrentIndex(0)
        if index == 1: # 点击“烟台”按钮时显示“牟平”
            self.stack.setCurrentIndex(4)
        if index == 2: # 点击“威海”按钮时显示“双岛湾”
            self.stack.setCurrentIndex(5)


    def showBigWidget(self):
        print(self)
        if self.sender().text() == "国悦府":
            self.stack.setCurrentIndex(0)
        if self.sender().text() == "桃花峪":
            self.stack.setCurrentIndex(1)
        if self.sender().text() == "罗汉崖":
            self.stack.setCurrentIndex(2)
        if self.sender().text() == "天外村":
            self.stack.setCurrentIndex(3)
        if self.sender().text() == "牟平":
            self.stack.setCurrentIndex(4)
        if self.sender().text() == "双岛湾":
            self.stack.setCurrentIndex(5)
    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWidget()
    sys.exit(app.exec_())