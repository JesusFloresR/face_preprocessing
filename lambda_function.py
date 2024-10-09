import json
import cv2
import requests
import imutils

import os
os.environ['TORCH_HOME'] = '/tmp'

initialized = False
detector = None

def initModule():
  global initialized
  global detector

  if initialized:
     return
  import face_detection
  detector = face_detection.build_detector("RetinaNetMobileNetV1", confidence_threshold = 0.5, nms_iou_threshold = 0.3)
  initialized = True

def extract_face(img):
    frame = imutils.resize(img, width=640)
    auxFrame = frame.copy()
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # print(img)
    detections = detector.detect(frame)
    faces = []
    face = None
    xmin_ = None
    ymin_ = None
    xmax_ = None
    ymax_ = None

    if len(detections)==0:
        return face, xmin_, ymin_, xmax_, ymax_
    
    for xmin,ymin,xmax,ymax,precision in detections:
        xmin_, ymin_, xmax_, ymax_ = xmin, ymin, xmax, ymax
        # print(ymin,ymax,xmin,xmax)
        face = auxFrame[int(ymin):int(ymax),int(xmin):int(xmax)]
        face = cv2.resize(face,(150,150),interpolation=cv2.INTER_CUBIC)
        faces.append([face, xmin_, ymin_, xmax_, ymax_])
    
    return faces

def save_face(url, img, name):
    # print(img)
    face, xmin, ymin, xmax, ymax = extract_face(img)[0]
    # Convertir la imagen a bytes
    _, buffer = cv2.imencode('.jpg', face)
    image_bytes = buffer.tobytes()

    response = requests.put(url, data=image_bytes, headers={'Content-Type': 'image/jpg'})

    # if not os.path.exists(path):
    #     os.makedirs(path)
    # cv2.imwrite(path + '/' + name + '.jpg',face)
    return xmin, ymin, xmax, ymax


def handler(event, context):
    try:
        print('Iniciando la lambda')
        initModule()
        url = 'https://7eo8t81vd3.execute-api.us-east-2.amazonaws.com/service-generate-presigned-url'
        print(url)
        s3=event['Records'][0]['s3']
        bucket=s3['bucket']['name']
        key=s3['object']['key']
        # bucket='vigilenteye-faces-video'
        # key='6/video/user_test.mp4'
        key_fragments=key.split('/')
        id=key_fragments[0]
        name=key_fragments[-1].split('.')[0]
        data = {
            'method': 'get_object',
            'id': int(id),
            'name': name,
            'bucket': bucket,
            'key': id + '/video/' + name + '.mp4'
        }

        response = requests.post(url, json=data)
        url_presigned = response.json()
        print(url_presigned)
        video = cv2.VideoCapture(url_presigned)
        print(video)
        num_img = 1
        iterator = 0
        print('Extrayendo frames del rostro')
        while True:
            iterator += 1
            check,frame = video.read()

            if iterator % 3 == 0:
                data = {
                    'method': 'put_object',
                    'id': int(id),
                    'name': name,
                    'content_type': 'image/jpg',
                    'bucket': bucket,
                    'key': id + '/images/' + name + str(num_img) + '.jpg'
                }

                response = requests.post(url, json=data)
                url_presigned = response.json()
                
                frame_copy = frame.copy()

                xmin_, ymin_, xmax_, ymax_ = save_face(url_presigned, frame_copy, name + str(num_img))
                num_img += 1

            if num_img == 11:
                break
        video.release()
        print('Finalizacion de la extraccion del rostro')

        return {
            'statusCode': 200,
            'body': 'ok'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }