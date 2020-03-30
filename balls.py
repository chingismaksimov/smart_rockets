import pygame
import random
import math
from pygame.locals import *
import numpy as np
from scipy.interpolate import interp1d
import sys
import copy
import vectors_module


pygame.init()

fps = 30

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

colors = [red, green, blue]

displayWidth = 700
displayHeight = 700

centerX = math.floor(displayWidth / 2)
centerY = math.floor(displayHeight / 2)

displaySurface = pygame.display.set_mode((displayWidth, displayHeight))
clock = pygame.time.Clock()

# Initialize the starting position of the members
initialX = centerX
initialY = centerY

# Initialize the starting position of the target
targetX = 10
targetY = 600

# Initialize the step size
lowerStep = -4
upperStep = 5

# Initialize the radius of the members
radius = 4

# Below are the global variables that can be changed
mutationRate = 0.01
populationSize = 25
dnaLength = 400


def main():

    global radius, colors, initialX, initialY, targetX, targetY, mutationRate, populationSize, dnaLength, lowerStep, upperStep

    target = Target()

    population = initialPopulation()

    while True:

        displaySurface.fill(white)
        target.draw()
        for i in range(populationSize):
            population.members[i].move(target)
            population.members[i].draw()
        population.checkState()
        population.evolvePopulation()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(fps)


class Population:
    def __init__(self):
        self.members = None
        self.highestFit = None
        self.totalFit = None
        self.matingPool = []
        self.children = []
        self.populationState = 'alive'

    def checkState(self):
        membersState = []
        for i in range(populationSize):
            membersState.append(self.members[i].state)

        if 'alive' not in membersState:
            print(self.totalFit)
            self.populationState = 'dead'

    def evolvePopulation(self):
        if self.populationState == 'dead':

            fitnessScores = []
            self.matingPool = []
            self.children = []

            for i in range(populationSize):
                fitnessScores.append(self.members[i].fitness)
            self.highestFit = max(fitnessScores)
            self.totalFit = sum(fitnessScores)

            for i in range(populationSize):
                numberOfAppereances = math.floor(100 * self.members[i].fitness / (self.totalFit + 0.1))
                self.matingPool = self.matingPool + [self.members[i].dna.structure] * numberOfAppereances

            for i in range(populationSize):
                parent1Dna = DNA()
                parent2Dna = DNA()
                parent1Dna.structure = random.choice(self.matingPool)
                parent2Dna.structure = random.choice(self.matingPool)
                child = crossover(parent1Dna, parent2Dna)
                child.mutate()
                self.children.append(child)

            self.members = [Member() for i in range(populationSize)]

            for i in range(populationSize):
                self.members[i].dna = self.children[i]

            self.populationState = 'alive'


class Member:
    def __init__(self):
        self.x = initialX
        self.y = initialY
        self.color = random.choice(colors)
        self.state = 'alive'
        self.fitness = 0
        self.dna = DNA()
        self.count = 0

    def draw(self):
        pygame.draw.circle(displaySurface, self.color, (self.x, self.y), radius, 0)

    def move(self, target):
        if self.x > 0 and self.x < displayWidth and self.y > 0 and self.y < displayHeight and self.state == 'alive' and self.count < dnaLength:
            self.x += self.dna.structure[self.count][0]
            self.y += self.dna.structure[self.count][1]
            self.count += 1
        else:
            self.state = 'dead'
            self.count = 0
            self.fitness = 1 / calcDistance(self, target)


class DNA:
    def __init__(self):
        self.structure = [(np.random.randint(lowerStep, upperStep), np.random.randint(lowerStep, upperStep)) for i in range(dnaLength)]

    def mutate(self):
        for i in range(len(self.structure)):
            if np.random.random() < mutationRate:
                self.structure[i] = (np.random.randint(lowerStep, upperStep), np.random.randint(lowerStep, upperStep))


class Target:
    def __init__(self):
        self.x = targetX
        self.y = targetY

    def draw(self):
        pygame.draw.rect(displaySurface, black, (self.x, self.y, 20, 20))


def initialPopulation():
    population = Population()
    population.members = [Member() for i in range(populationSize)]
    return population


def crossover(dna1, dna2):
    dna = DNA()
    midpoint = np.random.randint(1, dnaLength)
    dna.structure = dna1.structure[:midpoint] + dna2.structure[midpoint:]
    return dna


def calcDistance(obj1, obj2):
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    return math.sqrt(dx ** 2 + dy**2) + 0.1


if __name__ == '__main__':
    main()
