import cv2
import mediapipe as mp
import time
from sys import exit
import pygame

WIDTH = 1080
HEIGHT = 720
WEBCAM_WIDTH = 200
WEBCAM_HEIGHT = 160

fps = 30
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0) # Some devices, 0 

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils # Handles drawing lines across each landmark point

webcam_surface = pygame.Surface((WEBCAM_WIDTH, WEBCAM_HEIGHT))

while True:
    success, img = cap.read()
    img.flags.writeable = False # improves performance since we're passing by reference
    img = cv2.flip(img, 1)

    # Send in the RGB image to the model
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Extract the results, each hand
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLandmarks, mpHands.HAND_CONNECTIONS)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cv2image = cv2.resize(img, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
    