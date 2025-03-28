import pygame
import sys

pygame.init()

h=800
w=800
scroll_x=0

screen= pygame.display.set_mode((h,w))

clock= pygame.time.Clock()

title= pygame.display.set_caption('Mario Game')
screen.fill((255,255,255))

class Player:
    def __init__(self,x,y):
        self.size = (40,60)
        self.rect=pygame.Rect((x,y), self.size)
        self.position= (100,h-125)
        self.vel =[0,0]
        self.speed = 5
        self.jump = -15
        self.gravity = 1
        self.onGround= False
    
    def input(self,keys):
        if keys[pygame.K_LEFT]:
            self.vel[0] =-self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel[0] = self.speed
        else:
            self.vel[0]=0
        
        if keys[pygame.K_SPACE] and self.onGround:
            self.vel[1] = self.jump
            self.onGround= False
    
    def apply_physics(self,platforms):
        self.vel[1]

    def draw (self,surface, scroll_x):
        pygame.draw.rect(surface,(0,0,220), (self.rect.x - scroll_x, self.rect.y, self.rect.width, self.rect.height))

class Enemy:
    def __init__(self,x,y, width= '40', height = '40'):
        self.rect= pygame.Rect(x,y, width, height)

    def draw(self,surface, scroll_x):
        pygame.draw.rect(surface, (220,0,0),(self.rect.x - scroll_x, self.rect.y, self.rect.width, self.rect.height))

platforms = [
    pygame.Rect(0, h-40, 2000, 40),
    pygame.Rect(300,h-150, 100, 20),
    pygame.Rect(600, h-300, 200, 20),
    pygame.Rect(900, h-400, 200, 20)
]

player=Player(100,h-150)
enemies= [Enemy(500, h-150), Enemy(800, h-90), Enemy(1000,h-90)]

running= True


while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
    keys= pygame.key.get_pressed()
    player.input(keys)
    
    player.apply_physics(platforms)
    
    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            print("Game Over")
            running = False

    scroll_x = player.rect.x - w // 2

    for plat in platforms:
        pygame.draw.rect(screen,(0,255,0), plat)
        
    for plat in platforms:
        plat_rect=plat.copy()

    player.draw(screen, scroll_x)           
    pygame.display.flip()





