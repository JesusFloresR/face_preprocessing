import json
from save_face import save_face
import cv2
import requests

def lambda_handler(event, context):
    try:
        url = 'https://7eo8t81vd3.execute-api.us-east-2.amazonaws.com/service-generate-presigned-url'
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
        cv2.destroyAllWindows()
        print('Finalizacion de la extraccion del rostro')

        return {
            'statusCode': 200,
            'body': 'ok'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }