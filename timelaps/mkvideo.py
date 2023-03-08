import cv2
import os
import shutil
import time
import boto3
import re

"""
parameta
"""
frame_size = -1  #FHD=0, 4K=1
frame_rate = 30.0  #FPS

"""
end
"""

""" size set"""
if frame_size == 0:
    #FHD Timelaps動画用
    width = 1920
    height = 1080
elif frame_size ==1:
    #4K Timelasp動画用
    width = 3840
    height = 2160
else:
    #小さめに作る
    width = 640
    height = 360

""" """
def handler(event, context):
    s3 = boto3.resource('s3')
    bucket_name = "torch-image-corrected"
    bucket = s3.Bucket(bucket_name)
    objs = bucket.objects.all()
    timelaps(objs)

def timelaps(images):
    
    
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    video = cv2.VideoWriter('timelaps.mp4', fourcc, frame_rate, (width, height))
    #指定の画像ファイルでタイムラプスを作成
    for i in range(15):
        for i in images:
            #ファイル指定
            res1 = re.match(".{9}[0-3].07-20.+",i.key)
            res2 = re.match(".{9}[0-3].11-20.+",i.key)
            res3 = re.match(".{9}[0-3].15-20.+",i.key)
            if res1 or res2 or res3:
            　　#タイムラプスを作成
                bucket = s3.Bucket("torch-image-corrected")
                print(i.key)
                currentDate = i.key.split('/')[0]
                currentTime = i.key.split('/')[1]
                local_path = currentDate + '-' + currentTime
                bucket.download_file(i.key, local_path)
                img = cv2.imread(local_path)
                img = cv2.resize(img,(width,height))
                video.write(img)
        
    video.release()
    #タイムラプスをバケットに格納
    bucket2 = s3.Bucket('torch-timelaps')
    bucket2.upload_file('timelaps.mp4', 'timelaps.mp4')
    #print("画像の総枚数{0}".format(len(objs)))
  