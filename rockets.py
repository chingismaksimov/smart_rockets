import pygame
import numpy as np
from pygame.locals import *
import random
import vectors_module
import sys
import math


pygame.init()

fps = 30

displayWidth, displayHeight = 700, 700

centerX = math.floor(displayWidth / 2)
centerY = math.floor(displayHeight / 2)

initialX = centerX
initialY = displayHeight - 20
radius = 5

targetX = centerX
targetY = 40
targetRadius = 10

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

clock = pygame.time.Clock()
displaySurface = pygame.display.set_mode((displayWidth, displayHeight))

dnaLength = 600
mutationRate = 0.02
populationSize = 100

accelerationMagnitude = 0.4
closenessRate = 1
longevityRate = 1 - closenessRate


def main():

    target = Target()
    population = initialPopulation()
    obstacle1 = pygame.Rect(200, 200, 300, 50)
    obstacle2 = pygame.Rect(150, 500, 100, 100)
    obstacle3 = pygame.Rect(450, 500, 100, 100)

    while True:

        displaySurface.fill(black)

        for i in range(populationSize):
            population.members[i].move(target, obstacle1, obstacle2, obstacle3)
            population.members[i].draw()

        target.draw()
        pygame.draw.rect(displaySurface, blue, obstacle1)
        pygame.draw.rect(displaySurface, blue, obstacle2)
        pygame.draw.rect(displaySurface, blue, obstacle3)

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
        self.state = 'alive'
        self.totalFit = None
        self.matingPool = []
        self.children = []
        self.generation = 1

    def checkState(self):
        memberStates = []
        for i in range(populationSize):
            memberStates.append(self.members[i].state)
        if 'alive' not in memberStates:
            print('Generation number %s fitness is %s' % (self.generation, self.totalFit))
            self.state = 'dead'

    def evolvePopulation(self):
        if self.state == 'dead':

            memberFitnessScores = []

            for i in range(populationSize):
                memberFitnessScores.append(self.members[i].fitness)
            self.totalFit = sum(memberFitnessScores)

            for i in range(populationSize):
                numberOfAppearances = math.floor(self.members[i].fitness * 1000 / (self.totalFit))
                self.matingPool = self.matingPool + [self.members[i].dna.structure] * numberOfAppearances

            for i in range(populationSize):
                parent1Dna = DNA()
                parent2Dna = DNA()
                parent1Dna.structure = random.choice(self.matingPool)
                parent2Dna.structure = random.choice(self.matingPool)
                child = crossover(parent1Dna, parent2Dna)
                child.mutate()
                self.children.append(child)

            self.members = [Rocket() for i in range(populationSize)]

            for i in range(populationSize):
                self.members[i].dna = self.children[i]

            self.state = 'alive'
            self.matingPool = []
            self.children = []
            self.generation += 1


class Rocket:
    def __init__(self):
        self.position = vectors_module.vector_create(initialX, initialY)
        self.velocity = vectors_module.vector_create(0, 0)
        self.acceleration = vectors_module.vector_create(0, 0)
        self.dna = DNA()
        self.state = 'alive'
        self.count = 0
        self.fitness = 0

    def applyForce(self, force):
        self.acceleration.addTo(force)
        self.acceleration.multiplyBy(accelerationMagnitude)

    def move(self, target, obstacle1, obstacle2, obstacle3):
        if self.position.get_x() > 0 and self.position.get_x() < displayWidth and self.position.get_y() > 0 and self.position.get_y() < displayHeight and self.count < dnaLength and calcDistance(self, target) >= 15 and not obstacle1.collidepoint(self.position.get_x(), self.position.get_y()) and not obstacle2.collidepoint(self.position.get_x(), self.position.get_y()) and not obstacle3.collidepoint(self.position.get_x(), self.position.get_y()):
            self.applyForce(self.dna.structure[self.count])
            self.velocity.addTo(self.acceleration)
            self.position.addTo(self.velocity)
            self.count += 1
            self.acceleration.multiply(0)
        elif calcDistance(self, target) < 15:
            self.state = 'dead'
            self.fitness = (1 / calcDistance(self, target)) * 1.5 * 0.8 + longevityRate * self.count
            self.count = 0
        elif obstacle1.collidepoint(self.position.get_x(), self.position.get_y()) and obstacle2.collidepoint(self.position.get_x(), self.position.get_y()) and obstacle3.collidepoint(self.position.get_x(), self.position.get_y()):
            self.state = 'dead'
            self.fitness = (1 / calcDistance(self, target)) * closenessRate + longevityRate * self.count
            self.count = 0
        else:
            self.state = 'dead'
            self.fitness = (1 / calcDistance(self, target)) * closenessRate + longevityRate * self.count
            self.count = 0

    def draw(self):
        if self.state == 'alive':
            pygame.draw.circle(displaySurface, white, (math.floor(self.position.get_x()), math.floor(self.position.get_y())), radius)


class DNA:
    def __init__(self):
        self.structure = [vectors_module.createRandom2d() for i in range(dnaLength)]

    def mutate(self):
        for i in range(dnaLength):
            if np.random.random() < mutationRate:
                self.structure[i] = vectors_module.createRandom2d()


class Target:
    def __init__(self):
        self.position = vectors_module.vector_create(targetX, targetY)

    def draw(self):
        pygame.draw.circle(displaySurface, red, (math.floor(self.position.get_x()), math.floor(self.position.get_y())), targetRadius)


class Obstacle:
    pass


def crossover(dna1, dna2):
    dna = DNA()
    midpoint = np.random.randint(1, dnaLength)
    dna.structure = dna1.structure[:midpoint] + dna2.structure[midpoint:]
    return dna


def calcDistance(obj1, obj2):
    dx = obj1.position.get_x() - obj2.position.get_x()
    dy = obj1.position.get_y() - obj2.position.get_y()
    return math.sqrt(dx ** 2 + dy ** 2)


def initialPopulation():
    population = Population()
    population.members = [Rocket() for i in range(populationSize)]
    return population


if __name__ == '__main__':
    main()
