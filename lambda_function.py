import json
import cv2
import requests
import imutils
import boto3

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

def get_retina_face_mobilenet():
    id = '6'
    name = ''
    bucket = 'vigilanteye-models'
    # bucket='vigilenteye-faces-video'
    key='RetinaFace_mobilenet025.pth'
    data = {
        'method': 'get_object',
        'id': int(id),
        'name': name,
        'bucket': bucket,
        'key': key
    }

    url = 'https://7eo8t81vd3.execute-api.us-east-2.amazonaws.com/service-generate-presigned-url'

    response = requests.post(url, json=data)
    url_presigned = response.json()
    print(url_presigned)
    return requests.get(url_presigned)

def handler(event, context):
    try:
        print('Iniciando la lambda')
        destination_directory = '/tmp/hub/checkpoints'
        # source_file = '/var/task/RetinaFace_mobilenet025.pth'
        response = get_retina_face_mobilenet()
        if response.status_code == 200:
            # Asegúrate de que el directorio /tmp existe
            print('creando')
            os.makedirs(destination_directory, exist_ok=True)
            print('creo')

            # Guarda el contenido en un archivo local
            with open(destination_directory + '/RetinaFace_mobilenet025.pth', 'wb') as f:
                f.write(response.content)
            print(f'Archivo descargado y guardado en {destination_directory}')
        else:
            print('Error al descargar el archivo:', response.status_code)

        # shutil.move('/var/task/RetinaFace_mobilenet025.pth', '/tmp/hub/checkpoints/')
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
            'key': id + '/video/' + name + '/' + name + '.mp4'
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

            if iterator % 2 == 0:
                data = {
                    'method': 'put_object',
                    'id': int(id),
                    'name': name,
                    'content_type': 'image/jpg',
                    'bucket': bucket,
                    'key': id + '/images/' + name + '/' + name + str(num_img) + '.jpg'
                }

                response = requests.post(url, json=data)
                url_presigned = response.json()
                
                frame_copy = frame.copy()

                xmin_, ymin_, xmax_, ymax_ = save_face(url_presigned, frame_copy, name + str(num_img))
                num_img += 1

            if num_img == 151:
                break
        video.release()
        print('Finalizacion de la extraccion del rostro')

        payload = {
            'user_id': id
        }

        lambda_client = boto3.client('lambda')

        # Invoca la función Lambda
        response = lambda_client.invoke(
            FunctionName='vigilanteye_train_model',
            InvocationType='Event',  # Para no esperar la respuesta
            Payload=json.dumps(payload)
        )

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
    