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
max_fitness = 0
FUCK_FACTOR = 2
RANDOM_GENE_FACTOR = 250
MEMORY_SIZE = 15
FLAP = 1
NO_FLAP = 0

"""-----------Control Panel------------"""
FPS = 120
VELOCITY = 0.15
BLOCKS_SPEED = 4
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
        # print type(self.Flaps_Info_Array), type(self.Flaps_Results_Array)
        self.clf = self.clf.fit(self.Flaps_Info_Array, self.Flaps_Results_Array)
    def predict(self, data):
        a, b = data
        return self.clf.predict([[a, b]])
class Bird:
    def __init__(self, id):
        self.id = id
        self.bird_image = pygame.image.load("images/flappybird.png")
        self.dead_image = pygame.image.load("images/flappybird_dead.png")
        self.flap_force = BIRD_FLAP_FORCE
        self.speed = 0
        self.tilt = 0
        self.rect = pygame.Rect(W/3, H/4, 36, 28)
        self.passed_pipe = False
        self.score = 0
        self.alive = True
        self.mind = FlappyLearn()
        self.fitness = 0

    def calculate_fitness(self, pipes):
        global max_fitness
        if self.alive:
            self.fitness = FrameCount - abs(self.rect.y - pipes.info_rect.y)
            if self.fitness > max_fitness:
                max_fitness = self.fitness

    def kill(self):
        self.alive = False
        self.bird_image = self.dead_image

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
            bird.mind.add_random_training_data(MEMORY_SIZE)
            bird.mind.fit()

    def elitism_selection(self):
        # getting the two most fittest birds of the current generation
        return sorted(self.birds, key=lambda x: x.fitness, reverse=True)[:2]

    # CrossOver
    # Taking the two most fittest birds, and returning their demon love children
    def love(self, female_bird, male_bird):
            female_genes = (female_bird.mind.Flaps_Info_Array, female_bird.mind.Flaps_Results_Array)
            male_genes = (male_bird.mind.Flaps_Info_Array, male_bird.mind.Flaps_Results_Array)

            """After Some Time... *CENSORED*... And The Seed Is IN!"""
            """Now, Mixing Some Genes"""
            # two point crossover
            # selecting two random points at the bird memory
            genes_chain_len = len(female_genes[0])
            slice_indexes = (randint(0, int(genes_chain_len / 2)), randint(int(genes_chain_len/ 2), genes_chain_len) )
            # possible that last random index needs to be 1 less ??

            # mixing the genes for two new babies
            first_baby_genes = []
            for i in range(2):
                first_baby_genes.append(female_genes[i][:slice_indexes[0]] + \
                                        male_genes[i][slice_indexes[0]:slice_indexes[1]] + \
                                        female_genes[i][slice_indexes[1]:genes_chain_len])

            second_baby_genes = []
            for i in range(2):
                second_baby_genes.append(male_genes[i][:slice_indexes[0]] + \
                                        female_genes[i][slice_indexes[0]:slice_indexes[1]] + \
                                        male_genes[i][slice_indexes[1]:genes_chain_len])

            # returning the babies, separated from their parents at birth,
            # in the form of a tuple containing two lists
            return (first_baby_genes, second_baby_genes)

    # fucking them up a bit with freshly random generated genes
    def fuck_them_up_a_bit(self, children):
        for child_gene_chains in children:
            child_info_chain = child_gene_chains[0]
            child_result_chain = child_gene_chains[1]

            for i in range(FUCK_FACTOR):
                # selecting random gene to alter
                random_index = randint(0,len(child_info_chain))
                for i, info_gene in enumerate(child_info_chain):
                    if i == random_index:
                        child_info_chain[i] = [randint(0-RANDOM_GENE_FACTOR, RANDOM_GENE_FACTOR), randint(0-RANDOM_GENE_FACTOR, RANDOM_GENE_FACTOR)]
                        child_result_chain[i] = [randint(NO_FLAP, FLAP)]

    # Creating new generation of birds by using,
    # 1. Elitism Selection
    # 2. Two Points CrossOver
    # 3. Mutation
    def advance_generation(self):
        global bird_id, FrameCount
        FrameCount = 0
        new_birds = []

        # selecting two most fittest birds
        woman_bird, man_bird = self.elitism_selection()

        for i in range(int(self.num_of_birds / 2)):
            # making them fall in love, and taking their children, repeatedly
            children_genes = self.love(woman_bird, man_bird)
            # then mutating a bit of their genes for a finale
            self.fuck_them_up_a_bit(children_genes)

            for i in range(2):
                bird = Bird(bird_id)
                bird.mind.Flaps_Info_Array = children_genes[i][0]
                bird.mind.Flaps_Results_Array = children_genes[i][1]

                bird.mind.fit()
                new_birds.append(bird)
                bird_id += 1

        self.current_generation += 1
        self.birds = new_birds

    def alive_birds(self):
        return [bird for bird in self.birds if bird.alive]

def do_physics(bird):
    # bird falling and flapping physics
    if bird.alive:
        bird.speed -= VELOCITY
        bird.rect.y -= bird.speed

        if bird.speed > -90:
            bird.tilt = bird.speed * BIRD_ANDGLE_FACTOR
    elif bird.rect.x > 0- bird.rect.width:
        bird.rect.x -= BLOCKS_SPEED
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

    generation = score_font.render("Generation: " + str(evo.current_generation) + " | Max Fitness: " + str(max_fitness), False, SKY_BLUE)
    gameDisplay.blit(generation, (W/ 4, H - 70))

    for index ,bird in enumerate(fittest_birds):
        color = BLACK
        if not bird.alive: color = RED
        bird_surface = score_font.render("Bird #"+str(bird.id) + " Score: " + str(bird.score) + " Fitness:"+ str(bird.fitness), False, color)
        gameDisplay.blit(bird_surface, (0, index * 25))


"""------------ MAIN --------------"""
def main():
    global FrameCount
    init_pygame()

    # Creating Birds
    evo = Evolution(10)
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
            # if bird.alive:
            do_physics(bird)
            bird.draw()

            # if pipe is out of screen, deletes it
            # and creating a new one
            if pipes.X <= 0 - PIPE_HEAD_WIDTH:
                pipes = PipeSet()
                bird.passed_pipe = False
                if len(evo.alive_birds()) == 0:
                    evo.advance_generation()

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

    pygame.quit()
    sys.exit()


main()
