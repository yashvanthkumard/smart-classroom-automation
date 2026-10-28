import cv2
import numpy as np
import time
import RPi.GPIO as GPIO

# ---------------- GPIO ----------------
ZONE1_PIN = 17
ZONE2_PIN = 27
RELAY_ACTIVE_LOW = True
OFF_DELAY = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ZONE1_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(ZONE2_PIN, GPIO.OUT, initial=GPIO.HIGH)


def relay_on(pin):
    GPIO.output(pin, GPIO.LOW if RELAY_ACTIVE_LOW else GPIO.HIGH)

def relay_off(pin):
    GPIO.output(pin, GPIO.HIGH if RELAY_ACTIVE_LOW else GPIO.LOW)

relay_off(ZONE1_PIN)
relay_off(ZONE2_PIN)

# ---------------- YOLO FILES ----------------
CFG = "/home/pi/smart_classroom/yolo/yolov4-tiny.cfg"
WEIGHTS = "/home/pi/smart_classroom/yolo/yolov4-tiny.weights"
NAMES = "/home/pi/smart_classroom/yolo/coco.names"

with open(NAMES, "r") as f:
    classes = [line.strip() for line in f.readlines()]

net = cv2.dnn.readNet(WEIGHTS, CFG)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

if not cap.isOpened():
    GPIO.cleanup()
    exit()

last_seen_zone1 = 0
last_seen_zone2 = 0

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (640, 480))
    h, w = frame.shape[:2]
    mid = w // 2

    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    zone1_detected = False
    zone2_detected = False

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if classes[class_id] == "person" and confidence > 0.5:
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                bw = int(detection[2] * w)
                bh = int(detection[3] * h)

                x = int(center_x - bw / 2)
                y = int(center_y - bh / 2)

                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 255), 2)
                cv2.putText(frame, "Person", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                if center_x < mid:
                    zone1_detected = True
                else:
                    zone2_detected = True

    now = time.time()

    if zone1_detected:
        last_seen_zone1 = now
    if zone2_detected:
        last_seen_zone2 = now

    zone1_active = (now - last_seen_zone1) <= OFF_DELAY
    zone2_active = (now - last_seen_zone2) <= OFF_DELAY

    if zone1_active:
        relay_on(ZONE1_PIN)
    else:
        relay_off(ZONE1_PIN)

    if zone2_active:
        relay_on(ZONE2_PIN)
    else:
        relay_off(ZONE2_PIN)

    cv2.line(frame, (mid, 0), (mid, 480), (255, 0, 0), 3)

    cv2.putText(frame, f"ZONE 1: {'ON' if zone1_active else 'OFF'}", (30, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if zone1_active else (0, 0, 255), 2)

    cv2.putText(frame, f"ZONE 2: {'ON' if zone2_active else 'OFF'}", (350, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if zone2_active else (0, 0, 255), 2)

    cv2.imshow("Smart Classroom Automation (YOLO)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
