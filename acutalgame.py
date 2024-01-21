import pygame
from pygame.locals import *

# Machine vision imports
import cv2
import mediapipe as mp
import time
from sys import exit

import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

# To generate a wall 
import random

TOTAL_HITS = 0

WALL_SPEED = 12 
WALL_CONSTANT = 0.03 # The higher the number, the more frequent walls spawn

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

WEBCAM_WIDTH = int(SCREEN_WIDTH / 2)
WEBCAM_HEIGHT = int(SCREEN_HEIGHT / 5)

PUNCH_DELAY = 0.4
current_time = 1.0

PUNCH_DISTANCE = 0.1
PUNCH_DURATION = 4

GAME_HAS_STARTED = False

STRIKE_DISTANCE = 20

# counter for punch anmiation
is_punching = False

fps = 30
clock = pygame.time.Clock()
wall = None

pygame.font.init()

font = pygame.font.Font(None, 36)

# Load sprite sheet
sprite_sheet = pygame.image.load('./spirtes/BananaManSpriteSheet240by192.png')  # Replace with the path to your sprite sheet
sprite_width, sprite_height = 190, 190 
frames = [sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)) for i in range(4)]
frame_index = 0
character_rect = pygame.Rect(SCREEN_WIDTH / 3 - 160, SCREEN_HEIGHT - 300, sprite_width, sprite_height)

# Loading the punch sprite sheet
punch_sprite_sheet = pygame.image.load('./spirtes/bananaPunchSpriteSheet.png')  # Replace with the path to your sprite sheet
punch_sprite_width, punch_sprite_height = 190, 190 
punch_frames = [punch_sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)) for i in range(4)]
punch_frame_index = 0
# punch_character_rect = pygame.Rect(SCREEN_WIDTH / 3 - 160, SCREEN_HEIGHT - 300, sprite_width, sprite_height)

# Set up the title overlay
overlay_image = cv2.imread('./assets/title.png', cv2.IMREAD_UNCHANGED)
overlay_alpha = overlay_image[:, :, 3]

# LOADING STATIC IMAGES
bg = pygame.image.load('./assets/background.jpg')
ground = pygame.image.load('./assets/ground.png')

### MACHINE VISION WINDOW STUFF

cap = cv2.VideoCapture(0) # Some devices, 0 opens a mobile device :(

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence = 0.5)
mpDraw = mp.solutions.drawing_utils # Handles drawing lines across each landmark point

webcam_surface = pygame.Surface((WEBCAM_WIDTH, WEBCAM_HEIGHT))

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
print(classNames)

while not GAME_HAS_STARTED:

    # Do some stuff to detect a hand, start the game when the hand is detected
    success, img = cap.read()
    x, y, z = img.shape

    # Flip the frame vertically
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(imgRGB)

    className = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                # print(id, lm)
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)

                landmarks.append([lmx, lmy])

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(img, handslms, mpHands.HAND_CONNECTIONS)

            # Predict gesture
            prediction = model.predict([landmarks])
            # print(prediction)
            classID = np.argmax(prediction)
            className = classNames[classID]
    
    if className == 'thumbs up':
        GAME_HAS_STARTED = True


    # Show the final output
    cv2.putText(img, 'Give a Thumbs-Up to start the game!', (100, 100), cv2.FONT_HERSHEY_PLAIN, 
                   5, (0,255,0), 7)
    cv2.imshow("Output", img) 
    cv2.waitKey(1)

hands = mpHands.Hands()
cv2.destroyAllWindows()


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Banana Punch")
punch_frame = 4

class Wall:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = WALL_SPEED

    def update(self):
        self.rect.x -= self.speed

    def hasHitPlayer(self):
        return self.rect.x <= SCREEN_WIDTH / 3 and not is_punching # REPLACE WITH WHEREEVER THE PLAYER IS
    
    def withinStrikingRangeOfBanana(self):
        return self.rect.x - (SCREEN_WIDTH / 3 + 95) <= STRIKE_DISTANCE
    
    def swap_to_broken(self):
        # Load the broken wall image and update the image attribute
        self.image = pygame.image.load('./assets/brokenwall.png').convert()
    
    
# Generate the image of the wall
wall = Wall(SCREEN_WIDTH, 0, './assets/wall.jpg')

while GAME_HAS_STARTED:
    screen.blit(bg, (0,0))
    #draw ground (MAKE SCROLLING AFTER)
    screen.blit(ground, (0,630))

    if wall:
        wall.update()
        screen.blit(wall.image, wall.rect)
        if wall.hasHitPlayer():
            wall = None
    elif random.random() < WALL_CONSTANT:
        wall = Wall(SCREEN_WIDTH, 0, './assets/wall.jpg')

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

    current_time = current_time + 0.01
    
    # Extract the results, each hand
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLandmarks, mpHands.HAND_CONNECTIONS)
            knuckle = handLandmarks.landmark[9] # Corresponds to the 9th landmark

            if abs(knuckle.z) >= PUNCH_DISTANCE and current_time > PUNCH_DELAY: # Not actually PUNCH_DISTANCE CUZ BIGGER NUMBER IS CLOSER TO THE SCREEN
                # change this to attack later
                print('This is the z value: ', knuckle.z)
                # See if the wall is close enough to the object
                if wall:
                    print(wall.rect.x)
                    print(wall.withinStrikingRangeOfBanana())
                    if wall.withinStrikingRangeOfBanana():
                        TOTAL_HITS += 1
                        ## CALL SWAP IMG FUNCTION HERE
                        wall.swap_to_broken()
                        wall
                        
                is_punching = True
                punch_counter = PUNCH_DURATION
                current_time = 0
                
    # LOGIC FOR WHICH SPRITE TO DRAW   
    if is_punching: 
        if punch_counter > 0:
            screen.blit(punch_frames[frame_index], character_rect.topleft)
            punch_counter -= 1
        else:
            # reset punching state
            is_punching = False
    else:
        # draw walking sprite
        screen.blit(frames[frame_index], character_rect.topleft)
    # inc frame_index
    frame_index = (frame_index + 1 ) % 4

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) ## Since pygame and opencv uses different rgb channels
    cv2image = cv2.resize(img, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
    pygame.surfarray.blit_array(webcam_surface, cv2image.swapaxes(0, 1)) # Does some swapping so that the format matches that of pygame               

    # Attach the webcam_surface to the display, using block image transfer
    screen.blit(webcam_surface, (SCREEN_WIDTH - WEBCAM_WIDTH, 0)) # Put the webcam in the top right

    text = font.render("Total Walls Broken: " + str(TOTAL_HITS), True, (255, 255, 255))
    wall_pov = font.render("Wall POV: ", True, (255, 255, 25) )

    text_rect = text.get_rect(topleft=(0, 0))
    text_rect2 = wall_pov.get_rect(topleft = (100, 20))

    screen.blit(text, text_rect)
    screen.blit(wall_pov, text_rect2)


    pygame.display.update()
    
    clock.tick(fps)