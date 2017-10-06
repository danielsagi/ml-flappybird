import pygame
from random import randint
import sys

"""         Globals            """
"""----------------------------"""
exit = False
#
gameDisplay = None
Clock = None
#
BLACK = (0,0,0)
WHITE = (255,255,255)
#
H = 600
W = 800
FPS = 100
#
BLOCK_WIDTH = 20
"""-----------------------------"""

class Bird:
    def __init__(self):
        self.myimage = pygame.image.load("car.png")
        self.myimage.convert()
        self.x = 400
        self.y = 300
        self.height = 30
        self.width = 50
        self.color = BLACK
        self.flap_force = 5
        self.speed = 0

    def do_flap(self):
        self.speed = self.flap_force

    def draw(self):
        picture = pygame.transform.scale(self.myimage, (self.width,self.height))
        #pygame.draw.rect(gameDisplay, self.color, [self.x, self.y , self.width, self.height])
        gameDisplay.blit(picture, (self.x,self.y,self.width,self.height))


"""
Block Set, Contains information about a block set,
And in charge of calculating a random opening at initializing
"""
class BlockSet:
    def __init__(self):
        self.opening_size = randint(125, 175)

        # calculating random opening, Both of down block and up block.
        self.up_height = randint(0, H-self.opening_size)
        self.down_height = H - self.up_height - self.opening_size

        #starting from edge
        self.X = W
        self.color = BLACK

    def draw_blocks(self):
        # Up Block
        pygame.draw.rect(gameDisplay, self.color, [self.X, 0, BLOCK_WIDTH, self.up_height])
        # Down Block
        pygame.draw.rect(gameDisplay, self.color, [self.X, H - self.down_height, BLOCK_WIDTH, self.down_height])

    def move_block(self, offset):
        self.X -= offset


def events(bird):
    global exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.do_flap()

def keys(bird):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        bird.y -=1
    if keys[pygame.K_DOWN]:
        bird.y += 1

def do_gravity(bird):
    velocity = 0.15

    # speed always decreasing
    bird.speed -= velocity
    bird.y -= bird.speed

def init_pygame():
    global gameDisplay, Clock
    gameDisplay = pygame.display.set_mode((W, H))
    Clock = pygame.time.Clock()
    pygame.init()

"""             MAIN               """
"""--------------------------------"""
def main():
    init_pygame()
    bird = Bird()

    blockSets = []
    while not exit:
        gameDisplay.fill(WHITE)
        keys(bird)
        events(bird)

        if len(blockSets) == 0:
            blockSets.append(BlockSet())

        for blockSet in blockSets:
            if blockSet.X <= 0 - BLOCK_WIDTH:
                blockSets.remove(blockSet)
            else:
                blockSet.move_block(1)
                blockSet.draw_blocks()

        #do_gravity(bird)
        bird.draw()

        pygame.display.update()
        Clock.tick(FPS)

    pygame.quit()
    sys.exit()

main()


