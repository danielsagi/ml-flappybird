import pygame
import sys
import numpy

from sklearn import tree
from random import randint

"""----------------------------------FLAPPY BIRD-----------------------------------------
------------------------------------BY: DANIEL SAGI-----------------------------------"""
FrameCount = 0
exit = False
#
pygame.font.init()
score_font = pygame.font.SysFont('Comic Sans MS', 30)
game_over_font = pygame.font.SysFont('Comic Sans MS', 45)
background = pygame.image.load("images/bg.png")

gameDisplay = None
Clock = None
#
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
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
bird_id = 0
miles_count = 0

"""-----------Control Panel------------"""
FPS = 100
VELOCITY = 0.15
BLOCKS_SPEED = 3
BACK_MOVIE_SPEED = 1
BIRD_ANDGLE_FACTOR = 3.1
BIRD_FLAP_FORCE = 5
MIN_PIPE_OPENING = 160
MAX_PIPE_OPENING = 160
"""------------------------------------"""

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
            gameDisplay.blit(self.head, (x - PIPE_HEAD_OFFSET / 2,
                                         self.body_height,
                                         PIPE_HEAD_WIDTH,
                                         PIPE_HEAD_HEIGHT))
        else:
            gameDisplay.blit(self.body, (x, H - self.body_height, BLOCKS_WIDTH, self.body_height))
            gameDisplay.blit(self.head, (x - (PIPE_HEAD_OFFSET / 2),
                                         H - self.body_height - PIPE_HEAD_HEIGHT,
                                         PIPE_HEAD_WIDTH,
                                         PIPE_HEAD_HEIGHT))
class PipeSet:
    def __init__(self):
        self.opening_size = randint(MIN_PIPE_OPENING, MAX_PIPE_OPENING)
        self.behind_bird = False

        # calculating random opening, Both of down block and up block.
        self.up_height = randint(0, H - self.opening_size)
        self.down_height = H - self.up_height - self.opening_size

        # creating pipes
        self.up_pipe = Pipe(self.up_height, True)
        self.down_pipe = Pipe(self.down_height, False)

        # starting from edge
        self.X = W + randint(0, 100)
        self.up_pipe_rect = pygame.Rect(self.X, 0, BLOCKS_WIDTH, self.up_height)
        self.down_pipe_rect = pygame.Rect(self.X, H - self.down_height, BLOCKS_WIDTH, self.down_height)

        self.info_rect = pygame.Rect(self.X + BLOCKS_WIDTH / 2, self.up_height + self.opening_size / 2, 3, 3)

    def draw_blocks(self):
        self.up_pipe.draw(self.X)
        self.down_pipe.draw(self.X)
        # pygame.draw.rect(gameDisplay, BLACK, self.info_rect)

    def move_block(self, offset):
        self.X -= offset
        self.up_pipe_rect.x -= offset
        self.down_pipe_rect.x -= offset
        self.info_rect.x -= offset

    def is_colliding_bird(self, bird):
        # check_up_rect = pygame.Rect(self.up_pipe_rect.x, self.up_pipe_rect.y, self.up_pipe_rect.height, self.up_pipe_rect.width)
        # check_down_rect = pygame.Rect(self.down_pipe_rect.x, self.down_pipe_rect.y, self.down_pipe_rect.height, self.down_pipe_rect.width)
        return self.up_pipe_rect.colliderect(bird.rect) or self.down_pipe_rect.colliderect(bird.rect)
class Movie:
    def __init__(self, image):
        self.source_image = image
        self.source_rect = image.get_rect(y=H - image.get_rect().height)
        self.tape = []
        self.tape.append(self.source_rect)

    def roll_display(self):
        for image_rect in self.tape:
            # adding image to back when first starts to go off screen
            if image_rect.x < 0 and len(self.tape) < 2:
                # new_rect = self.source_image.get_rect(x=self.source_image.get_rect().width)
                new_rect = pygame.Rect(self.source_rect.width - 1, self.source_rect.y, self.source_rect.width,
                                       self.source_rect.height)
                self.tape.append(new_rect)

            if image_rect.x < 0 - image_rect.width:
                self.tape.remove(image_rect)

            image_rect.x -= BACK_MOVIE_SPEED
            gameDisplay.blit(self.source_image, image_rect)

class FlappyLearn:
    def __init__(self):
        self.clf = tree.DecisionTreeClassifier()
        self.Flaps_Info_Array = []
        self.Flaps_Results_Array = []

    def add_random_training_data(self, quantity):
        for i in range(quantity):
            self.add_to_training_data(( randint(-500, 500), randint(-500, 500), randint(0,1)))
    def add_to_training_data(self, data):
        a, b, value = data
        self.Flaps_Info_Array.append([a, b])
        self.Flaps_Results_Array.append([value])
    def clear_training_data(self):
        self.Flaps_Info_Array = []
        self.Flaps_Results_Array = []

    def fit(self):
        self.clf = self.clf.fit(self.Flaps_Info_Array, self.Flaps_Results_Array)
    def predict(self, data):
        a, b = data
        return self.clf.predict([[a, b]])

class Bird:
    def __init__(self, id):
        self.id = id
        self.bird_image = pygame.image.load("images/flappybird.png")
        self.flap_force = BIRD_FLAP_FORCE
        self.speed = 0
        self.tilt = 0
        self.rect = pygame.Rect(W/3, H/3, 36, 28)
        self.passed_pipe = False
        self.score = 0
        self.alive = True
        self.mind = FlappyLearn()
        self.fitness = 0

    def calculate_fitness(self, pipes):
        self.fitness = FrameCount

    def kill(self):
        self.alive = False

    def do_flap(self):
        self.speed = self.flap_force

    def is_passed_pipe(self, pipe):
        if pipe.X + BLOCKS_WIDTH <= self.rect.x and self.passed_pipe == False:
            self.passed_pipe = True
            return True
        else:
            return False

    def distance_from_pipe(self, pipes):
        return self.rect.x - pipes.info_rect.x

    def draw(self):
        picture = pygame.transform.scale(self.bird_image, (self.rect.width, self.rect.height))
        picture = pygame.transform.rotate(picture, self.tilt)
        gameDisplay.blit(picture, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

class Evolution():
    def __init__(self, num_of_birds):
        global bird_id
        self.num_of_birds = num_of_birds
        self.birds = []

        for i in range(self.num_of_birds):
            self.birds.append(Bird(bird_id))
            bird_id += 1

        self.current_generation = 0

    def do_first_generation(self):
        for bird in self.birds:
            bird.mind.add_random_training_data(15)
            bird.mind.fit()


    def new_generation(self):

    def alive_birds(self):
        return [bird for bird in self.birds if bird.alive]

def do_physics(bird):
    # bird falling and flapping physics
    bird.speed -= VELOCITY
    bird.rect.y -= bird.speed

    if bird.speed > -90:
        bird.tilt = bird.speed * BIRD_ANDGLE_FACTOR

def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
def init_pygame():
    global gameDisplay, Clock
    gameDisplay = pygame.display.set_mode((W, H))
    Clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird - Daniel Sagi")
    icon = pygame.image.load("images/icon.png")
    pygame.display.set_icon(icon)

    pygame.init()
def print_stats(evo):
    fittest_birds = sorted(evo.birds, key=lambda x: x.fitness, reverse=True)[:5]
    for index ,bird in enumerate(fittest_birds):
        color = BLACK
        if not bird.alive: color = RED
        bird_surface = score_font.render("Bird #"+str(bird.id) + " Fitness:"+ str(bird.fitness), False, color)
        gameDisplay.blit(bird_surface, (0, index * 25))


"""------------ MAIN --------------"""
def main():
    global FrameCount
    init_pygame()

    # Creating Birds
    evo = Evolution(50)
    evo.do_first_generation()

    back_movie = Movie(background)
    pipes = PipeSet()
    while True:
        # Visuals
        gameDisplay.fill(SKY_BLUE)
        back_movie.roll_display()
        FrameCount += 1

        pipes.move_block(BLOCKS_SPEED)
        pipes.draw_blocks()

        for bird in evo.birds:
            if bird.alive:
                do_physics(bird)
                bird.draw()

                # if pipe is out of screen, deletes it
                # and creating a new one
                if pipes.X <= 0 - BLOCKS_WIDTH:
                    pipes = PipeSet()
                    bird.passed_pipe = False
                # if normal state, moves the pipe left
                else:
                    horizontal_distance = pipes.info_rect.x - bird.rect.x
                    vertical_distance = pipes.info_rect.y - bird.rect.y

                    # collision detection between bird and pipes or
                    # if bird is out of boundaries of screen
                    if pipes.is_colliding_bird(bird) or bird.rect.y >= H + bird.rect.height or bird.rect.y <= 0-bird.rect.height * 2:
                        bird.kill()
                    # bird passed the pipe successfully
                    if bird.is_passed_pipe(pipes):
                        bird.score += 1
                        if bird.distance_from_pipe(pipes) <= 50:
                            pass #

                    if all(bird.mind.predict((horizontal_distance, vertical_distance))):
                        bird.do_flap()

                    bird.calculate_fitness(pipes)

        print_stats(evo)
        pygame.display.update()
        Clock.tick(FPS)

        if events() == "QUIT": break
        if len(evo.alive_birds()) == 0: break

    pygame.quit()
    sys.exit()


main()
