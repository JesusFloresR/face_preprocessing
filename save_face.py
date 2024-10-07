from extract_face import extract_face
import cv2
import requests

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