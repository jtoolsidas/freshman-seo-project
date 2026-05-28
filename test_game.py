import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blue Sky and Green Grass Background")

BLUE_SKY = (135, 206, 235)
GREEN_GRASS = (34, 139, 34)

GRASS_HEIGHT = 200
grass_y_position = SCREEN_HEIGHT - GRASS_HEIGHT


clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #game logic here

    screen.fill(BLUE_SKY)
   
    pygame.draw.rect(screen, GREEN_GRASS, (0, grass_y_position, SCREEN_WIDTH, GRASS_HEIGHT))
    pygame.display.flip()


    clock.tick(60)

pygame.quit()
sys.exit()