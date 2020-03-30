import vectors_module
import math
import numpy as np


class Particle:

    def __init__(self):
        self.position = None
        self.velocity = None
        self.mass = 1

    def move(self):
        self.position.addTo(self.velocity)

    def accelerate(self, acceleration):
        # where acceleration is a vector
        self.velocity.addTo(acceleration)

    def angleTo(self, anotherParticle):
        dx = anotherParticle.position.get_x() - self.position.get_x()
        dy = anotherParticle.position.get_y() - self.position.get_y()
        return np.arctan2(dy, dx)

    def distanceTo(self, anotherParticle):
        dx = self.position.get_x() - anotherParticle.position.get_x()
        dy = self.position.get_y() - anotherParticle.position.get_y()
        return math.sqrt(dx**2 + dy**2)

    def gravitateTo(self, anotherParticle):
        #This will gravitate our particle to anotherParticle
        gravity = vectors_module.vector_create(0, 0)
        distance = self.distanceTo(anotherParticle)
        gravity.set_length(anotherParticle.mass / (distance ** 2))
        gravity.set_angle(self.angleTo(anotherParticle))
        self.velocity.addTo(gravity)


def particle_create(x, y, speed, direction):
    particle = Particle()
    particle.position = vectors_module.vector_create(x, y)
    particle.velocity = vectors_module.vector_create(0, 0)
    particle.velocity.set_length(speed)
    particle.velocity.set_angle(direction)
    return particle
