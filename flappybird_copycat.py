import pygame
import sys
import numpy

from sklearn import tree
from random import randint

"""----------------------------------FLAPPY BIRD-----------------------------------------
------------------------------------BY: DANIEL SAGI-----------------------------------"""

"""
Instructions:
SPACE - jump
C - continue
S - start AI
R - reset memory of AI

Program works as follows:
You start playing, (by pressing the space bar)
and at which point you feel satisfied by your performance, you press - S
Now the AI will start imitating you, as you played before.
Do not worry too much about failing, the AI will erase any failure made by you. (or at least the obvious ones)

(If you are really bad at this game, there is no need for you to restart, only to press the - R,
to reset to AI memory)

When you see a Game Over message, just press - C to continue.

"""


Score = 0
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
Start_ML = False
DIFF_FACTOR = 25

"""-----------Control Panel------------"""
FPS = 100
BLOCKS_SPEED = 3
BACK_MOVIE_SPEED = 1
BIRD_ANDGLE_FACTOR = 3.1
BIRD_FLAP_FORCE = 5
MIN_PIPE_OPENING = 160
MAX_PIPE_OPENING = 160
"""------------------------------------"""

class Bird:
    def __init__(self):
        self.x = W / 3
        self.y = H / 3
        self.bird_image = pygame.image.load("images/flappybird.png")
        self.height = 28
        self.width = 36
        self.color = BLACK
        self.flap_force = BIRD_FLAP_FORCE
        self.speed = 0
        self.tilt = 0
        self.bird_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def do_flap(self):
        self.speed = self.flap_force

    def draw(self):
        picture = pygame.transform.scale(self.bird_image, (self.width, self.height))
        picture = pygame.transform.rotate(picture, self.tilt)
        gameDisplay.blit(picture, (self.x, self.y, self.width, self.height))
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
        pygame.draw.rect(gameDisplay, BLACK, self.info_rect)

    def move_block(self, offset):
        self.X -= offset
        self.up_pipe_rect.x -= offset
        self.down_pipe_rect.x -= offset
        self.info_rect.x -= offset

    def is_colliding_bird(self, bird):
        return self.up_pipe_rect.colliderect(bird.bird_rect) or self.down_pipe_rect.colliderect(bird.bird_rect)

    def is_behind_bird(self, bird):
        if self.X + BLOCKS_WIDTH < bird.x and self.behind_bird == False:
            self.behind_bird = True
            return True
        else:
            return False
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
        self.move_removed = False
        self.last_index = 0

    # Method adds given data to training data, if the last inserted data is not similar
    def condition_add_to_training_data(self, bird, pipes, data):
        horizontal_distance, vertical_distance, value = data
        # subtracting current info from last, and only inserting new information if the values are much different
        if FrameCount % 5 == 0 and len(self.Flaps_Info_Array):
            diff = numpy.subtract(self.Flaps_Info_Array[len(self.Flaps_Info_Array) - 1],
                                  (horizontal_distance, vertical_distance))
            if abs(diff[0]) > DIFF_FACTOR and abs(diff[1]) > DIFF_FACTOR:
                self.Flaps_Info_Array.append([horizontal_distance, vertical_distance])
                self.Flaps_Results_Array.append([value])
                print("Auto Add: ", value)

                # if a new insertion has taken place, refitting the tree
                self.fit()
    def add_to_training_data(self, data):
        horizontal_distance, vertical_distance, value = data
        self.Flaps_Info_Array.append([horizontal_distance, vertical_distance])
        self.Flaps_Results_Array.append([value])
        if value == 1: print("Added Clap")

    def remove_wrong_move_from_training_data(self):
        """ Removing all data after wrong move, including the move itself """
        self.Flaps_Results_Array = self.Flaps_Results_Array[:self.last_index -3]
        self.Flaps_Info_Array = self.Flaps_Info_Array[:self.last_index -3]
        print("Loser At: " + str(self.last_index) + " End At: " + str(len(self.Flaps_Info_Array)))

        self.move_removed = True
    def clear_training_data(self):
        self.Flaps_Info_Array = []
        self.Flaps_Results_Array = []

    def fit(self):
        self.clf = self.clf.fit(self.Flaps_Info_Array, self.Flaps_Results_Array)
    def predict(self, data):
        a, b = data
        return self.clf.predict([[a, b]])

def events(bird):
    global Start_ML
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.do_flap()
                return "CLAP"
            if event.key == pygame.K_s:
                Start_ML = not Start_ML
            if event.key == pygame.K_c:
                return "CONTINUE"
            if event.key == pygame.K_r:
                return "RESET"

def do_physics(bird):
    velocity = 0.15

    # bird falling and flapping physics
    bird.speed -= velocity
    bird.y -= bird.speed
    bird.bird_rect.y = bird.y

    if bird.speed > -90:
        bird.tilt = bird.speed * BIRD_ANDGLE_FACTOR

def game_over_stall(bird, pipes, copy_mind):
    global Score
    while True:
        gameover_surface = game_over_font.render("Game Over!", False, (0, 255, 0))
        gameDisplay.blit(gameover_surface, (W / 2 - 120, H / 3))

        event = events(bird)
        if event == "QUIT":
            pygame.quit()
            sys.exit()
        elif event == "CONTINUE":
            Score = 0
            bird.y = H / 3
            bird.speed = 3
            break

        if not copy_mind.move_removed:
            copy_mind.remove_wrong_move_from_training_data()

        pygame.display.update()
    copy_mind.move_removed = False

def init_pygame():
    global gameDisplay, Clock
    gameDisplay = pygame.display.set_mode((W, H))
    Clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird - Daniel Sagi")
    icon = pygame.image.load("images/icon.png")
    pygame.display.set_icon(icon)

    pygame.init()
def print_stats(horizontal_distance, vertical_distance):
    horizontal_surface = score_font.render("horizontal: " + str(horizontal_distance), False, BLACK)
    vertical_surface = score_font.render("vertical: " + str(vertical_distance), False, BLACK)
    score_surface = score_font.render(" " + str(Score), False, BLACK)
    gameDisplay.blit(score_surface, (0, 0))
    gameDisplay.blit(horizontal_surface, (0, 30))
    gameDisplay.blit(vertical_surface, (0, 60))

def distance_from_pipe(bird, pipes):
    return bird.bird_rect.x - pipes.info_rect.x

"""------------ MAIN --------------"""
def main():
    global Score, FrameCount
    horizontal_distance, vertical_distance = 0, 0

    init_pygame()
    bird = Bird()
    back_movie = Movie(background)
    copy_mind = FlappyLearn()

    pipes = PipeSet()
    while True:
        # Visuals
        gameDisplay.fill(SKY_BLUE)
        back_movie.roll_display()
        do_physics(bird)
        bird.draw()
        FrameCount += 1

        # ML Calculations
        if not pipes.behind_bird:
            horizontal_distance = pipes.info_rect.x - bird.bird_rect.x
        vertical_distance = pipes.info_rect.y - bird.bird_rect.y

        print_stats(horizontal_distance, vertical_distance)

        # events
        event = events(bird)
        if event == "QUIT": break
        # adding current clapping data to training data
        elif event == "CLAP":
            copy_mind.add_to_training_data((horizontal_distance, vertical_distance, 1))
        elif event == "RESET":
            copy_mind.clear_training_data()
        else:
            copy_mind.condition_add_to_training_data(bird, pipes, (horizontal_distance, vertical_distance, 0))

        # if bird is out of boundaries of screen
        if bird.y >= H + bird.height:
            game_over_stall(bird, pipes, copy_mind)

        # bird passed the pipe successfully
        if pipes.is_behind_bird(bird):
            Score += 1
            if distance_from_pipe(bird, pipes) <= 50:
                copy_mind.last_index = len(copy_mind.Flaps_Info_Array) - 1
                print("Saved Last Index -", copy_mind.last_index)

        # if pipe is out of screen, deletes it
        # and creating a new one
        if pipes.X <= 0 - BLOCKS_WIDTH:
            pipes = PipeSet()

        # if normal state, moves the pipe left
        else:
            pipes.move_block(BLOCKS_SPEED)
            pipes.draw_blocks()

            # collision detection between bird and pipes
            if pipes.is_colliding_bird(bird):
                game_over_stall(bird, pipes, copy_mind)
                pipes = PipeSet()

        # AI mode, Ai now controls the movements
        if Start_ML:
            AI_surface = game_over_font.render("AI", False, (255, 0, 0))
            gameDisplay.blit(AI_surface, (W / 2 - 30, H / 4))

            predicted = copy_mind.predict((horizontal_distance, vertical_distance))
            if all(predicted):
                bird.do_flap()

        pygame.display.update()
        Clock.tick(FPS)

    pygame.quit()
    sys.exit()


main()
