import pygame

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([500,500])
x=0
y=0
import collections
stack = collections.deque()
stack.append("d")
stack.append("d")
for i in stack:
    print(i)
while True:
    for e in pygame.event.get():
        if(e.type == pygame.KEYDOWN):
            if(e.key == pygame.K_RIGHT):
                x+=5
            elif(e.key == pygame.K_LEFT):
                x-=5
            if(e.key == pygame.K_DOWN):
                y+=5
            elif(e.key == pygame.K_UP):
                y-=5
            pass
        pass
    screen.fill((255,0,0))
    
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(x,y,32,32))
    pygame.display.flip()
    clock.tick(30)