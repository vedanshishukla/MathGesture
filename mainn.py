import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import google.generativeai as genai
from PIL import Image
import streamlit as st
 
st.set_page_config(layout="wide")
st.image('Frame1.png')
 
col1, col2 = st.columns([3,2])
with col1:
    run = st.checkbox('Run', value=True)
    FRAME_WINDOW = st.image([])
 
with col2:
    output_text_area=st.title("Answer")
    output_text_area = st.subheader("")
 
genai.configure(api_key="")
model = genai.GenerativeModel('')
 
# Initialize the webcam to capture video
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
 
# Initialize the HandDetector class
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)
 
def getHandInfo(img):
    # Ensure the image is not empty
    if img is None or img.size == 0:
        raise ValueError("Empty image passed to getHandInfo")
    
    # Find hands in the current frame
    hands, img = detector.findHands(img, draw=False, flipType=True)
 
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        print(fingers)
        return fingers, lmList
    else:
        return None
 
def draw(info, prev_pos, canvas, img):
    fingers, lmList = info
    current_pos = None
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos
        cv2.line(canvas, tuple(current_pos), tuple(prev_pos), (255, 0, 255), 10)
    elif fingers == [1, 0, 0, 0, 0]:
        canvas = np.zeros_like(img)
 
    return current_pos, canvas
 
def sendToAI(model, canvas, fingers):
    if fingers == [1, 1, 1, 1, 0]:
        pil_image = Image.fromarray(canvas)
        response = model.generate_content(["Solve this math problem", pil_image])
        return response.text
 
prev_pos = None
canvas = None
image_combined = None
output_text = ""

while True:
    success, img = cap.read()
    if not success or img is None:
        print("Failed to capture image from webcam")
        continue  # Skip this frame and try again
 
    img = cv2.flip(img, 1)
 
    if canvas is None:
        canvas = np.zeros_like(img)
 
    info = getHandInfo(img)
    if info:
        fingers, lmList = info
        prev_pos, canvas = draw(info, prev_pos, canvas, img)
        output_text = sendToAI(model, canvas, fingers)
 
    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
    FRAME_WINDOW.image(image_combined, channels="BGR")
 
    if output_text:
        output_text_area.text(output_text)
 
    cv2.waitKey(1)
