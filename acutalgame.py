import pygame
from pygame.locals import *

# Machine vision imports
import cv2
import mediapipe as mp
import time
from sys import exit

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

WEBCAM_WIDTH = int(SCREEN_WIDTH / 2)
WEBCAM_HEIGHT = int(SCREEN_HEIGHT / 5)

#PUNCH_DELAY = ___
#PUNCH_DISTANCE = ___

GAME_HAS_STARTED = True

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Banana Punch")

fps = 30
clock = pygame.time.Clock()


### LOAD IMAGES AND SPIRTES
bg = pygame.image.load('./assets/background.jpg')
ground = pygame.image.load('./assets/ground.png')
### MACHINE VISION WINDOW STUFF

cap = cv2.VideoCapture(0) # Some devices, 0 opens a mobile device :(

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils # Handles drawing lines across each landmark point

webcam_surface = pygame.Surface((WEBCAM_WIDTH, WEBCAM_HEIGHT))

while not GAME_HAS_STARTED:
    # Do some stuff to detect a hand, start the game when the hand is detected
    print('hi')
while GAME_HAS_STARTED:
    # draw background
    screen.blit(bg, (0,0))

    #draw ground (MAKE SCROLLING AFTER)
    screen.blit(ground, (0,630))

    # draw and scroll the ground
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    # FIND THE HANDS 
    success, img = cap.read()
    img.flags.writeable = False # improves performance since we're passing by reference
    img = cv2.flip(img, 1)

    # Send in the RGB image to the model
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB) # Getting the solution

    # Extract the results, each hand
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLandmarks, mpHands.HAND_CONNECTIONS)
            knuckle = handLandmarks.landmark[9] # Corresponds to the 9th landmark
            print(knuckle)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) ## Since pygame and opencv uses different rgb channels

    cv2image = cv2.resize(img, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
    pygame.surfarray.blit_array(webcam_surface, cv2image.swapaxes(0, 1)) # Does some swapping so that the format matches that of pygame               

    # Attach the webcam_surface to the display, using block image transfer
    screen.blit(webcam_surface, (SCREEN_WIDTH - WEBCAM_WIDTH, 0)) # Put the webcam in the top right

    pygame.display.update()
    
    clock.tick(fps)

    if cv2.waitKey(1) == ord('q'):
        break