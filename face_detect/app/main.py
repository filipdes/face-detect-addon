import cv2
import requests
import numpy as np
import time
import paho.mqtt.client as mqtt
import base64
import json
import threading
from ftplib import FTP
from io import BytesIO
import os


response_lock = threading.Lock()
ha_response = None

def upload_face_ftp(server,username,pwd,face,filename):
    # Encode frame naar JPEG in geheugen
    success, encoded = cv2.imencode(".jpg", face)
    if not success:
        err("JPEG encoding failed")

    bio = BytesIO(encoded.tobytes())
    try:
        with FTP(server,timeout=5) as ftp:
            ftp.login(username, pwd)
            ftp.storbinary(f"STOR {filename}", bio)
    except Exception as E:
        err(f"problem with FTP connection:{E}")
    


def read_config():
     if os.path.exists("/data/options.json"):
        with open("/data/options.json", "r") as f:
            return json.load(f)
     info("test locally in virtual environment")
     with open("../data/options.json", "r") as f:
            return json.load(f)
     

def info(msg):
    print(f"Info: {msg}")

def warning(msg):
    print(f"Warning: {msg}")

def err(msg):
    print(f"Error: {msg}")
    
def on_mqtt_msg(client,userdata,msg):
    global ha_response
    with response_lock:
        ha_response = msg.payload.decode()

cfgs = read_config()
info("content config:" + str(cfgs))

cascade_csf = cv2.CascadeClassifier(cfgs['HAAR_DETECT'])
if cascade_csf.empty():
    err("cascade detection model empty")
else:
    info("cascade detection model loaded")

headers = {"Authorization": f"Bearer {cfgs['TOKEN']}"}

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(cfgs['MQTT_USER'],cfgs['MQTT_PWD'])
mqtt_client.connect(cfgs['MQTT_BROKER'],port=int(cfgs['MQTT_PORT']),keepalive=60)
mqtt_client.subscribe(cfgs['UNIQUE_PERSON_ID']+'/'+cfgs['MQTT_RESPONS_TOPIC'])
mqtt_client.on_message = on_mqtt_msg
mqtt_client.loop_start()

#register esp32_cam_mqtt_Facedetect in home assistant
mqtt_client.publish(
    cfgs['MQTT_DISCOVER_TOPIC']+"_"+cfgs['UNIQUE_PERSON_ID']+"/config",
    json.dumps({
        "name": "ESP32 Cam MQTT Facedetect "+cfgs['UNIQUE_PERSON_ID'],
        "unique_id": "esp32_cam_mqtt_facedetect_"+cfgs['UNIQUE_PERSON_ID'],
        "topic": cfgs['UNIQUE_PERSON_ID']+"/"+cfgs['MQTT_IMG_TOPIC'],
        "image_encoding": "b64"
    }),
    retain=True
)

# ======================
# State machine states
# ======================
STATE_IDLE = 0
STATE_CAPTURE = 1
STATE_PROCESS = 2
STATE_WAIT_RESPONSE = 3

state = STATE_IDLE
frame = None
gray = None
gray_crop = None
wait_counter = 0
num = 0

while True:

    # ======================
    # STATE: IDLE
    # ======================
    if state == STATE_IDLE:
        gray_crop = None
        state = STATE_CAPTURE


    # ======================
    # STATE: CAPTURE
    # ======================
    elif state == STATE_CAPTURE:
        try:
            resp = requests.get(cfgs["HA_URL"], headers=headers, timeout=2)

            if resp.status_code != 200:
                err(f"Snapshot failed ({resp.status_code})")
                time.sleep(1)
                state = STATE_IDLE
                continue

            arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as E:
            err(f"Error reading or converting image ({E})")
            time.sleep(1)
            state = STATE_IDLE
            continue

        state = STATE_PROCESS

    # ======================
    # STATE: PROCESS
    # ======================
    elif state == STATE_PROCESS:
        faces = cascade_csf.detectMultiScale(
            gray,
            scaleFactor=float(cfgs['HAAR_SCALE_FACTOR']),
            minNeighbors=int(cfgs['HAAR_MIN_NEIGHBOURS'])
        )

        if len(faces) > 0:
            if cfgs["DETECT_1_FACE"] == "on":
                (x, y, w, h) = faces[0]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                gray_crop = gray[y:y+h, x:x+w]
            else:
                x_s = [];y_s = []
                for (x,y,w,h) in faces:
                    x_s.append(x);y_s.append(y)
                    x_s.append(x+w);y_s.append(y+h)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                min_x = min(x_s);min_y = min(y_s)
                max_x = max(x_s);max_y = max(y_s)
                gray_crop = gray[min_y:max_y, min_x:max_x]
                    
            mqtt_client.publish(cfgs['UNIQUE_PERSON_ID']+"/"+cfgs['MQTT_TRIG_CNT_FACES_TOPIC'],
                                str(len(faces)),
                                retain=False)
        else:
            mqtt_client.publish(cfgs['UNIQUE_PERSON_ID']+"/"+cfgs['MQTT_TRIG_CNT_FACES_TOPIC'],
                                0,
                                retain=False)

        _, jpeg = cv2.imencode(".jpg", frame)
        mqtt_client.publish(
            cfgs['UNIQUE_PERSON_ID']+"/"+cfgs['MQTT_IMG_TOPIC'],
            base64.b64encode(jpeg.tobytes()).decode("utf-8"),
            retain=False
        )

        wait_counter = 0
        state = STATE_WAIT_RESPONSE


    # ======================
    # STATE: WAIT_RESPONSE
    # ======================
    elif state == STATE_WAIT_RESPONSE:
        with response_lock:
            cmd = ha_response

        if cmd == "save":
            info("save received")

            if gray_crop is not None:
                upload_face_ftp(
                    cfgs['FTP_SERVER'],
                    cfgs['FTP_USER'],
                    cfgs['FTP_PWD'],
                    gray_crop,
                    cfgs['UNIQUE_PERSON_ID'] +"_"+ str(num) + ".jpg"
                )
                num += 1

            with response_lock:
                ha_response = None

            state = STATE_IDLE

        elif cmd == "skip":
            info("skip received")

            with response_lock:
                ha_response = None

            state = STATE_IDLE

        else:
            time.sleep(0.25)
            wait_counter += 1

            if wait_counter > cfgs['TIMES_TO_WAIT']:
                info("No response → next frame")
                with response_lock:
                    ha_response = None
                state = STATE_IDLE
            
