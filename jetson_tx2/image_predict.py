import paho.mqtt.client as paho
import json
import ast
import numpy as np
from keras.preprocessing import image
from keras.applications import inception_v3
from keras import backend as K
import requests
import time
# import h5py as h5py

# Fix crash issue
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.9
config.gpu_options.visible_device_list = "0"
set_session(tf.Session(config=config))
K.clear_session()

# Fix crash issue
# Load pre-trained image recognition model

model = inception_v3.InceptionV3()

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    # mqtt_message = json.dumps(
    # {
    # "hash": hash,
    # "image_location": dst,
    # "color": color,
    # "robot": "resource:com.diy3.Robot#1152",
    # "asset": "resource:com.diy3.CapturedImage#"+str(ciid)})
    matches = msg.payload.decode("utf-8")
    matches = ast.literal_eval(matches)
    print(matches['color'])
    image_location = matches['image_location']
    asset = matches['asset']
    print(matches['image_location'])
    print(matches['robot'])
    print(matches['hash'])
    # think I am going to need to call classify_image.py

    img = image.load_img(image_location, target_size=(299, 299))
    input_image = image.img_to_array(img)

    # Scale the image so all pixel intensities are between [-1, 1] as the model expects
    input_image /= 255.
    input_image -= 0.5
    input_image *= 2.

    # Add a 4th dimension for batch size (as Keras expects)
    input_image = np.expand_dims(input_image, axis=0)

    # Run the image through the neural network
    predictions = model.predict(input_image)

    # Convert the predictions into text and print them
    predicted_classes = inception_v3.decode_predictions(predictions, top=1)
    imagenet_id, name, confidence = predicted_classes[0][0]
    print("This is a {} with {:.4}% confidence!".format(name, confidence * 100))

    nameLikelihood = confidence * 100
    nameLikelihood = str(round(nameLikelihood,2))+"%"
    objectName = name.encode('utf-8')

# send to composer-rest-server api

    time.sleep(5)
    url = "http://<URL>:3000/api/com.diy3.ClassifyTransaction"
    payload = "{\n \"$class\": \"com.diy3.ClassifyTransaction\",\n \"asset\": "'"'+asset+'"'",\n \"ai\": \"resource:com.diy3.AI#9230\",\n \"nameLikelihood\": "'"'+nameLikelihood+'"'",\n \"objectName\":"'"'+objectName+'"'" \n }"
  #  payload = "{\n \"$class\": \"com.diy3.ClassifyTransaction\",\n \"asset\":\""'"'+asset+'"'",\n \"ai\": \"resource:com.diy3.AI#9230\",\n \"nameLikelihood\": "'"'+nameLikelihood+'"'",\n \"objectName\": \""'"'+str(objectName)+'"'" \n}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    # completed api call
    print('send transaction to composer-rest-server')
    print('ready for the next image')


# mqtt variables
client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("<URL>", 1883)
client.subscribe("robotPayload/image-metadata", qos=1)

client.loop_forever()
