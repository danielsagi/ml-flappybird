import pygame
import sys
from random import randint

"""----------------------------------FLAPPY BIRD-----------------------------------------
------------------------------------BY: DANIEL SAGI-----------------------------------"""
Score = 0
exit = False
FrameRate = 0
#
pygame.font.init()
score_font = pygame.font.SysFont('Comic Sans MS', 30)
game_over_font = pygame.font.SysFont('Comic Sans MS', 45)
background = pygame.image.load("images/bg.png")

gameDisplay = None
Clock = None
#
BLACK = (0,0,0)
WHITE = (255,255,255)
SKY_BLUE = (0, 153, 204)
#
H = 650
W = 800
#
BLOCKS_WIDTH = 60
BLOCKS_SPACE = 350
PIPE_HEAD_HEIGHT = 30
PIPE_HEAD_OFFSET = 4
PIPE_HEAD_WIDTH = BLOCKS_WIDTH + PIPE_HEAD_OFFSET
#

"""-----------Control Panel------------"""
FPS = 120
BLOCKS_SPEED = 3
BACK_MOVIE_SPEED = 1
BIRD_ANDGLE_FACTOR = 3.1
BIRD_FLAP_FORCE = 5
MIN_PIPE_OPENING = 135
MAX_PIPE_OPENING = 160
"""------------------------------------"""

class Bird:
    def __init__(self):
        self.bird_image = pygame.image.load("images/flappybird.png")
        self.flap_force = BIRD_FLAP_FORCE
        self.speed = 0
        self.tilt = 0
        self.rect = pygame.Rect(W/3, H/4, 36, 28)

    def do_flap(self):
        self.speed = self.flap_force

    def draw(self):
        picture = pygame.transform.scale(self.bird_image, (self.rect.width,self.rect.height))
        picture = pygame.transform.rotate(picture, self.tilt)
        gameDisplay.blit(picture, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

    def is_collided_with_blocks(self, pipeSet):
        return

class Pipe:
    def __init__(self, height, isUp):
        self.body_height = height - PIPE_HEAD_HEIGHT

        # loading images and resizing them
        self.body = pygame.image.load("images/pipeBody.png")
        self.body = pygame.transform.scale(self.body, (BLOCKS_WIDTH, height))

        self.head = pygame.image.load("images/pipeHead.png")
        self.head = pygame.transform.scale(self.head, (BLOCKS_WIDTH + PIPE_HEAD_OFFSET, PIPE_HEAD_HEIGHT))

        self.isUp = isUp

    def draw(self, x):
        if self.isUp:
            gameDisplay.blit(self.body, (x, 0, BLOCKS_WIDTH, self.body_height))
            gameDisplay.blit(self.head, (x - PIPE_HEAD_OFFSET /2,
                                         self.body_height,
                                         PIPE_HEAD_WIDTH,
                                         PIPE_HEAD_HEIGHT))
        else:
            gameDisplay.blit(self.body, (x, H - self.body_height, BLOCKS_WIDTH, self.body_height))
            gameDisplay.blit(self.head, (x - (PIPE_HEAD_OFFSET/2),
                                         H-self.body_height-PIPE_HEAD_HEIGHT,
                                         PIPE_HEAD_WIDTH,
                                         PIPE_HEAD_HEIGHT))

class PipeSet:
    def __init__(self):
        self.opening_size = randint(MIN_PIPE_OPENING, MAX_PIPE_OPENING)
        self.behind_bird = False

        # calculating random opening, Both of down block and up block.
        self.up_height = randint(0, H-self.opening_size)
        self.down_height = H - self.up_height - self.opening_size

        # creating pipes
        self.up_pipe = Pipe(self.up_height, True)
        self.down_pipe = Pipe(self.down_height, False)

        #starting from edge
        self.X = W + PIPE_HEAD_WIDTH

        self.up_pipe_rect = pygame.Rect(self.X, 0, BLOCKS_WIDTH, self.up_height)
        self.down_pipe_rect = pygame.Rect(self.X, H - self.down_height, BLOCKS_WIDTH, self.down_height)


    def draw_blocks(self):
        self.up_pipe.draw(self.X)
        self.down_pipe.draw(self.X)

    def move_block(self, offset):
        self.X -= offset
        self.up_pipe_rect.x -= offset
        self.down_pipe_rect.x -= offset

    def is_colliding_bird(self, bird):
        return self.up_pipe_rect.colliderect(bird.rect) or self.down_pipe_rect.colliderect(bird.rect)

    def is_behind_bird(self, bird):
        if self.X + BLOCKS_WIDTH < bird.rect.x and self.behind_bird == False:
            self.behind_bird = True
            return True
        else:
            return False

class Movie:
    def __init__(self, image):
        self.source_image = image
        self.source_rect = image.get_rect(y=H-image.get_rect().height)
        self.tape = []
        self.tape.append(self.source_rect)
    def roll_display(self):
        for image_rect in self.tape:
            # adding image to back when first starts to go off screen
            if image_rect.x < 0 and len(self.tape) < 2:
                # new_rect = self.source_image.get_rect(x=self.source_image.get_rect().width)
                new_rect = pygame.Rect(self.source_rect.width-1, self.source_rect.y, self.source_rect.width, self.source_rect.height)
                self.tape.append(new_rect)

            if image_rect.x < 0 - image_rect.width:
                self.tape.remove(image_rect)

            image_rect.x -= BACK_MOVIE_SPEED
            gameDisplay.blit(self.source_image, image_rect)

def events(bird):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.do_flap()
                return "CLAP"

def do_physics(bird):
    velocity = 0.15

    # bird falling and flapping physics
    bird.speed -= velocity
    bird.rect.y -= bird.speed

    if bird.speed > -90:
        bird.tilt = bird.speed * BIRD_ANDGLE_FACTOR

def game_over_stall(bird):
    global Score
    while True:
        gameover_surface = game_over_font.render("Game Over!", False, (0, 255, 0))
        gameDisplay.blit(gameover_surface, (W/2 - 120, H/3))
        pygame.display.update()
        event = events(bird)
        if event == "QUIT":
            pygame.quit()
            sys.exit()
        elif event == "CLAP":
            Score = 0
            bird.y = H/3
            break

def init_pygame():
    global gameDisplay, Clock
    gameDisplay = pygame.display.set_mode((W, H))
    Clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird - Daniel Sagi")
    icon = pygame.image.load("images/icon.png")
    pygame.display.set_icon(icon)

    pygame.init()

"""------------ MAIN --------------"""
def main():
    global Score, FrameRate
    init_pygame()
    bird = Bird()
    back_movie = Movie(background)

    pipeSets = []
    while True:
        FrameRate += 1
        if events(bird) == "QUIT": break
        elif FrameRate % 99 == 0:
            pipeSets.append(PipeSet())


        # if bird is out of boundaries of screen
        if bird.rect.y >= H + bird.rect.height:
            game_over_stall(bird)
            pipeSets = []

        gameDisplay.fill(SKY_BLUE)

        back_movie.roll_display()
        do_physics(bird)

        bird.draw()

        score_surface = score_font.render(" " +str(Score), False, (0, 0, 0))
        gameDisplay.blit(score_surface, (0, 0))

        for pipeSet in pipeSets:
            if pipeSet.is_behind_bird(bird):
                Score += 1
            if pipeSet.X <= 0 - BLOCKS_WIDTH:
                pipeSets.remove(pipeSet)
            else:
                pipeSet.move_block(BLOCKS_SPEED)
                pipeSet.draw_blocks()
                if pipeSet.is_colliding_bird(bird):
                    game_over_stall(bird)
                    pipeSets = []

        pygame.display.update()
        Clock.tick(FPS)

    pygame.quit()
    sys.exit()

main()


