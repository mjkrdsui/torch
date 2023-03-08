import numpy as np
import cv2
import glob
import boto3
from time import sleep
from datetime import datetime

TMP_FOLDER_PATH = "./data/"
MTX_PATH = TMP_FOLDER_PATH + "mtx.csv"
DIST_PATH = TMP_FOLDER_PATH + "dist.csv"

# メイン関数
def handler(event, context):
    
    s3 = boto3.resource('s3')
    #PUTされた画像を取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    currentDate = file_name.split('/')[0]
    currentTime = file_name.split('/')[1]
    #Lambda上の一時保存ディレクトリに画像をダウンロード
    local_path = '/tmp/' + currentDate + '-' + currentTime
    bucket1 = s3.Bucket(bucket_name)
    bucket1.download_file(file_name, local_path)
    
    new_local_path = '/tmp/' + currentDate + '-' + currentTime + '-after'
    cv2.imwrite(new_local_path, calibrateImage(local_path))
    
    bucket2 = s3.Bucket('torch-image-distorted')
    bucket2.upload_file(new_local_path, file_name)

# カメラの歪みをCSVファイルを元に補正する関数
def calibrateImage(path):
    mtx, dist = loadCalibrationFile(MTX_PATH, DIST_PATH)

    img = cv2.imread(path)
    resultImg = cv2.undistort(img, mtx, dist, None) # 内部パラメータを元に画像補正
    sleep(1)
    return resultImg

# キャリブレーションCSVファイルを読み込む関数
def loadCalibrationFile(mtx_path, dist_path):
    try:
        mtx = np.loadtxt(mtx_path, delimiter=',')
        dist = np.loadtxt(dist_path, delimiter=',')
    except Exception as e:
        raise e
    return mtx, dist