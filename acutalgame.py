import pygame
from pygame_functions import *
from pygame.locals import *
pygame.init()


screenSize(1000,800)
setBackgroundImage("./assets/background.jpg")
pygame.display.set_caption("Running Game")

fps = 30
clock = pygame.time.Clock()


run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
               


pygame.display.update()

clock.tick(fps)