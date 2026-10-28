# Smart Classroom Automation System

## Project Overview
A Raspberry Pi-based smart classroom automation prototype that uses computer vision to detect people and control fans and lights in two classroom zones.

## Features
- Person detection using computer vision.
- Two-zone classroom monitoring.
- Automatic fan and light control using a relay module.
- Five-second delay before switching off appliances after a person leaves a zone.
- Live camera feed with detection boxes and zone status.

## Hardware
- Raspberry Pi 4 Model B
- USB webcam
- Four-channel relay module
- Two 12V DC fans
- Two 12V DC lights
- 12V DC power supply

## Technologies
- Python
- OpenCV
- NumPy
- YOLOv4-tiny
- Raspberry Pi GPIO

## Project Structure
- `smart_classroom.py` — Main automation program
- `camera_test.py` — Camera testing
- `relay_test.py` — Relay testing
- `models/` — Model files
- `tf_model/` — TensorFlow model files, if used
- `yolo/` — YOLO model files

## Working
The webcam captures video, and the detection model identifies people. The video frame is divided into two zones. The corresponding relay activates the fan and light when a person is detected. Appliances switch off after five seconds without a detection in their zone.

## Safety
This prototype uses 12V DC loads. Check relay ratings and wiring before operation. Never connect 12V directly to Raspberry Pi GPIO pins.

## Project Status
Academic mini-project prototype. Add actual test results and demonstration photographs after verification.
