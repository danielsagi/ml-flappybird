import pygame
import sys

class Bird:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.height = 20
        self.width = 20
        self.color = BLACK
        self.speed = 0

    def do_flap(self):
        self.speed = flap_force

    def draw(self):
        pygame.draw.rect(gameDisplay, self.color, [self.x, self.y , self.width, self.height])

def events():
    global exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

def keys(bird):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        bird.speed = 3


BLACK = (0,0,0)
WHITE = (255,255,255)
H = 600
W = 800
gameDisplay = pygame.display.set_mode((W, H))
FPS = 100
CLOCK = pygame.time.Clock()

flap_force = 20
velocity = 0.15


exit = False
def main():
    pygame.init()
    bird = Bird()


    while not exit:
        events()
        keys(bird)

        gameDisplay.fill(WHITE)

        # speed always decreasing
        bird.speed -= velocity
        bird.y -= bird.speed
        bird.draw()

        pygame.display.update()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()

main()
