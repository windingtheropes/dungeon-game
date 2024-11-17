import pygame

pygame.init()
clock = pygame.time.Clock()
game_screen = pygame.display.set_mode([500,500])

while True:
    pygame.display.flip()
    clock.tick(30)