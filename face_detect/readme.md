\# Face Detect



Deze add-on detecteert gezichten in camerabeelden en publiceert de resultaten via MQTT.



\## ⚙️ Installatie

1. Voeg deze repository toe aan Home Assistant
2. Installeer de Face Detect add-on
3. Configureer de opties
4. Start de add-on



\## 🔧 Configuratie

Voorbeeldconfiguratie:


    {
    "TOKEN":"Here Home Assistant long term token",
    "HA_URL":"http://Here Home Assistant hostname:8123/api/camera_proxy/Here ESP32 camera device created with ESPHome",
    "HAAR\_DETECT":"models/haarcascade_frontalface_default.xml",
    "HAAR_SCALE_FACTOR":1.2,
    "HAAR_MIN_NEIGHBOURS":3,  
    "UNIQUE_PERSON_ID":"personal id for classroom context",
    "MQTT_BROKER":"name broker",
    "MQTT_PORT":1883,
    "MQTT_USER":"username broker",
    "MQTT_PWD":"password broker",
    "MQTT_DISCOVER_TOPIC":"homeassistant/camera/esp32_cam_mqtt_facedetect",
    "MQTT_IMG_TOPIC":"img",
    "MQTT_RESPONS_TOPIC":"img/respons",
    "MQTT_TRIG_CNT_FACES_TOPIC":"faces/count",
    "TEST_ON_PC":0,
    "FTP_USER":"username FTP server",
    "FTP_PWD":"password FTP server",
    "FTP_SERVER":"host FTP server"
    }


## ▶️ Werking

* De add-on ontvangt beelden.
* Detecteert gezichten.
* Stuurt resultaten via MQTT.
  * Beeld met kader rond eerst gedetecteerd gezicht.
  * Boodschap met aanta l gedetecteerde gezichten.

## 🪵 Logs

Gebruik Log bekijken in Home Assistant voor debug-informatie.
