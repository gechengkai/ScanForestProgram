def fun(start,end):
    for i in range(start,end):
        print("self.num--", i)
        if i>600:
            print("--------------------------------------")
            fun(300,500)
            break
    
    
def setRange():
    with open("UI\\taian\\guoyuefu\\guoyuefu.range") as lines:
        for line in lines:
            line = line.strip('\n')#去掉换行符
            rangeList = line.split('\t')#按空格分割字符串
            start = rangeList[0]
            end = rangeList[1]
            tilt = rangeList[2]
            for i in range(int(start), int(end)):
                tempStr = str(i) + '#' + str(tilt) + '#' + "530"
                print(tempStr)

'''**********************文件上传测试**************************'''

import time,os
import requests
import json
import glob

def sendMsg(img_name):
    t = time.time()
    print("treeNum:%d"%int(round(t * 1)))
    postData = dict(treeNum=str(int(round(t * 1))), workContent = "普查", img1=img_name, equipment="37090200001311000980", source="摄像头")
    # print("postData:%s"%postData)
    postList = []
    postList.append(postData)
    print("postList:%s"%postList)
    urlStr = "http://112.245.48.4:8083/app/upload"
    try:
        responds = requests.post(urlStr, json=postList, timeout=(3,7))
    except:
        print('----------------------------------上传信息失败')
        responds = None
    if responds == None:
        print("上传信息失败:%s\n"%(json.loads(responds.text)))
        return None
    else:
        tempStr = json.loads(responds.text)
        print("tempStr.get(\"code\"):%s"%(tempStr.get("code")))
        if tempStr.get("code") == 200:
            print("上传信息成功:%s\n"%(json.loads(responds.text)))
            return 200
        else:
            print("上传信息失败:%s\n"%(json.loads(responds.text)))
            return None

def sendImg(img_path):
    urlStr = "http://112.245.48.4:8083/app/file_upload"
    image = {'files': (open(img_path, 'rb'))}
    try:
        response = requests.post(urlStr, files=image, timeout=(3,7))
    except:
        print('----------------------------------上传图片失败')
        response = None
    if response == None:
        print("上传图片失败:%s\n"%(json.loads(response.text)))
        return None
    else:
        tempStr = json.loads(response.text)
        print("tempStr.get(\"code\"):%s"%(tempStr.get("code")))
        if tempStr.get("code") == 200:
            print("上传图片成功:%s\n"%(json.loads(response.text)))
            return 200
        else:
            print("上传图片失败:%s\n"%(json.loads(response.text)))
            return None
def upload():
    t = time.time() 
    # timeStamp = str(int(round(t))) #时间戳
    RES_SAVE_PATH = 'E:\\ScanForestProgram\\detectDir\\taian\detect\\20210901-0941\\'#检测结果存放路径
    img_paths = glob.glob(os.path.join(RES_SAVE_PATH, '*.jpg')) #获取图片路径
    img_paths.sort() #排序
    for i in range(len(img_paths)):
        print("共%d张照片"%(len(img_paths)))
        print("上传第%d张照片"%i)
        if sendImg(img_paths[i]) == None:
            i -= 1
            continue
        else:
            tempList = img_paths[i].split("\\")
            img_name = tempList[-1]
            print("img_name:%s"%img_name)
            if sendMsg(img_name) == None:
                i -= 1
            print("第%d次上传结束\n\n"%i)
            continue
def test():
    RES_SAVE_PATH = 'E:\\ScanForestProgram\\detectDir\\taian\detect\\20210901-0904\\'#检测结果存放路径
    img_paths = glob.glob(os.path.join(RES_SAVE_PATH, '*.jpg')) #获取图片路径
    # os.path.split(fileUrl)
