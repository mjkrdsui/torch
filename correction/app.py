import boto3
import cv2
import time
import numpy as np

#指定の座標を修正する関数
def inpaint(src,top1,bottom1,top2,bottom2):
    mask = np.zeros((*src.shape[:-1],1), dtype=np.uint8)
    #より細かく補正範囲を指定するため、2回に分けて指定
    #一度に補正すると余計な個所も補正してしまうため
    mask1 = cv2.rectangle(mask, 
                        top1, 
                        bottom1, 
                        color=(255,255,255), 
                        thickness=cv2.FILLED
                        )
    mask2 = cv2.rectangle(mask1, 
                        top2, 
                        bottom2, 
                        color=(255,255,255), 
                        thickness=cv2.FILLED
                        )
    #こちらで補正
    dst = cv2.inpaint(src,mask2,5,cv2.INPAINT_TELEA)
    return dst

def handler(event, context):
    # s3から画像を取得しlambdaに保存
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
    #opencvで画像を編集し別のパスへ保存
    img = cv2.imread(local_path)
    dst1 = cv2.fastNlMeansDenoisingColored(img, h=10)
    #座標を指定する
    dst2 = inpaint(dst1, (0,600), (280,1080), (280,980), (550,1080))
    #編集後画像を別のディレクトリへ
    new_local_path = '/tmp/' + currentDate + '-' + currentTime + '-after'
    cv2.imwrite(new_local_path, dst2)
    #別のs3へ保存
    time.sleep(10)
    bucket2 = s3.Bucket('torch-image-corrected')
    bucket2.upload_file(new_local_path, file_name)
    return
    