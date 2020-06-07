import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np
import math


class Scene:
    """ OpenGL 2D scene class """
    # initialization

    def __init__(self, width, height):
        # time
        self.t = 0
        self.showVector = True
        self.point = np.array([0, 0])
        self.vector = np.array([10, 10])
        self.pointsize = 3
        self.width = width
        self.height = height
        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

    # step

    def step(self):
        # move point
        self.point = self.point + 0.1*self.vector

        # check borders
        if self.point[0] < -self.width/2:    # point hits left border
            # mirror at n = [1,0]
            n = np.array([1, 0])
            self.vector = self.mirror(self.vector, n)
        elif self.point[0] > self.width/2:    # point hits right border
            # mirrot at n = [-1,0]
            n = np.array([-1, 0])
            self.vector = self.mirror(self.vector, n)
        elif self.point[1] < -self.height/2:           # point hits upper border
            # mirrot at n = [0,1]
            n = np.array([0, 1])
            self.vector = self.mirror(self.vector, n)
        elif self.point[1] > self.height/2:  # point hits lower border
            # mirrot at n = [0,-1]
            n = np.array([0, -1])
            self.vector = self.mirror(self.vector, n)

        #print(self.point, self.vector)

    # mirror a vector v at plane with normal n

    def mirror(self, v, n):
        # normalize n
        normN = n / np.linalg.norm(n)
        # project negative v on n
        l = np.dot(-v, n)
        # mirror v
        mv = v + 2*l*n
        return mv

    # render

    def render(self):
        # render a point
        glBegin(GL_POINTS)
        glColor(0.0, 0.0, 1.0)
        glVertex2fv(self.point)
        glEnd()

        # render the vector starting at the point
        if self.showVector:
            glColor(1.0, 0.0, 0.0)
            glBegin(GL_LINES)
            # the line from the point to the end of the vector
            glVertex2fv(self.point)
            glVertex2fv(self.point+self.vector)

            # make an arrow at the tip of the vector
            normvector = self.vector/np.linalg.norm(self.vector)
            rotnormvec = np.array([-normvector[1], normvector[0]])
            p1 = self.point + self.vector - 6*normvector
            a = p1 + 3*self.pointsize/2*rotnormvec
            b = p1 - 3*self.pointsize/2*rotnormvec
            glVertex2fv(self.point+self.vector)
            glVertex2fv(a)
            glVertex2fv(self.point+self.vector)
            glVertex2fv(b)
            glEnd()
