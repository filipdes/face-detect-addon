# ESP32-CAM Face Detection with Home Assistant (MQTT Add-on)

Language: **English** | [Nederlands](readme_nl.md)

## Overview

This project demonstrates how to integrate computer vision (face detection) with Home Assistant using:

* an ESP32-CAM
* Python (OpenCV)
* MQTT
* a custom Home Assistant add-on

The add-on retrieves camera snapshots from Home Assistant, detects faces using a Haar Cascade model, publishes annotated images back to Home Assistant via MQTT, and optionally uploads detected faces to a FTP server.

This project is especially suited for educational purposes (adult education, vocational training, IoT / AI introduction).

## Educational Goals

This project helps students learn:

* How MQTT works in real-world applications
* How Home Assistant handles cameras and entities
* Basic computer vision concepts (face detection)
* Python application structure (state machines, threading)
* Client–server communication
* Add-on development for Home Assistant

No advanced AI knowledge is required.

## System Architecture

ESP32-CAM
↓ (camera stream)
Home Assistant
↓ (snapshot API)
Python Add-on
├─ Face detection (OpenCV)
├─ MQTT publish (image + data)
└─ FTP upload (detected faces)
↓
Home Assistant Dashboard \& Automations

## Requirements

### Hardware

* ESP32-CAM (configured via ESPHome)
* Home Assistant (Supervised / OS recommended)
* MQTT broker (e.g. Mosquitto)
* Optional: FTP server

### Software

* Home Assistant 2023+
* Python 3.10+
* OpenCV
* Paho-MQTT
* Requests
* NumPy

## Camera Integration

The camera is accessed via Home Assistant, not directly from Python.
The add-on uses the Home Assistant REST API:

&nbsp;   /api/camera\\\_proxy/camera.<camera\\\_entity>


This ensures:

* proper authentication
* no direct socket handling
* compatibility with ESPHome cameras

## MQTT Discovery

The add-on registers a camera entity automatically using MQTT Discovery:

´homeassistant/camera/<unique\_id>/config´

Example payload:

&nbsp;   {
    "name": "ESP32 Cam MQTT Facedetect",
    "unique\\\_id": "esp32\\\_cam\\\_facedetect\\\_student01",
    "image\\\_topic": "img/student01/frame",
    "image\\\_encoding": "b64"
    }


Important for classrooms!!
Each student must use:

* a unique unique\_id
* unique MQTT topics

Otherwise entities will overwrite each other when using the same mqtt broker.

## Face Detection

* OpenCV Haar Cascade
* Configurable parameters:

  * scaleFactor
  * minNeighbors

* Only the first detected face is processed (for simplicity)

Detected faces can:

* be drawn on the image
* be uploaded to an FTP server
* trigger automations via MQTT

## MQTT Events (Automation Friendly)

The add-on can publish extra MQTT messages, for example:


&nbsp;   student01/faces/count → 0, 1, 2, ...


This allows Home Assistant automations such as:

* turn on lights when a face is detected
* play a sound
* send a notification

No MQTT sensor is required; automations can trigger directly on MQTT messages.

## Configuration (Add-on)

When running as a Home Assistant add-on, configuration is handled via the UI.

The values are stored automatically in:


&nbsp;   /data/options.json


Typical options:

* MQTT broker credentials
* Haar cascade parameters
* FTP server settings
* Camera entity ID

For local testing, the same code can read a ../data/options.json file.

## Local Development vs Add-on

The application supports two modes:

    Mode	Description
    Local	Run in a Python virtual environment
    Add-on	Run inside Home Assistant

The data path is abstracted:

    BASE_PATH = "/data" if running_as_addon else "../data"

This allows seamless testing before deployment.

## Classroom Use

This project works very well in a classroom because:

** every student can use their own MQTT topic
** Home Assistant provides instant visual feedback
** concepts are concrete and observable
** students can extend the project themselves

Suggested assignments:

** change detection parameters
** add MQTT automations
** extend the state machine
** log detection statistics

## License

This project is intended for educational use.

You are free to:

** use
** modify
** extend
** teach with this project

Attribution is appreciated.

## Acknowledgements

** OpenCV community
** Home Assistant developers
** ESPHome project