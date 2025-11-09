import pygame
from pygame.locals import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

circle_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    screen.fill("gray")

    pygame.draw.circle(screen, "green", circle_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[K_w]:
        circle_pos.y -= 100 * dt
    if keys[K_s]:
        circle_pos.y += 100 * dt
    if keys[K_a]:
        circle_pos.x -= 100 * dt
    if keys[K_d]:
        circle_pos.x += 100 * dt

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()