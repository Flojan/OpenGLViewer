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
        self.vertices = []
        self.faces = []
        self.normals = []
        self.data = []
        self.boundingbox = []
        self.center = []
        self.scale = []

        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

    # read Object from File
    def readObject(self):
        if len(sys.argv) == 2:

            f = open(sys.argv[1])
            lines = f.readlines()

            for line in lines:
                if line:
                    # print(line.split()[1:])
                    # input()
                    if line.startswith('f'):  # Polygone
                        self.faces.append(line[1:])
                    if line.startswith('v'):  # Objekt-Punkte
                        self.vertices.append(
                            [float(v) for v in line.split()[1:]])
                    if line.startswith('vn'):  # Vertex-Normalen
                        self.normals.append(
                            [float(vn) for vn in line.split()[1:]])

            self.boundingbox = [list(map(min, zip(*self.vertices))),
                                list(map(max, zip(*self.vertices)))]
            self.center = [(x[0] + x[1]) / 2.0 for x in zip(*self.boundingbox)]
            self.scale = 2.0 / max([x[1] - x[0]
                                    for x in zip(*self.boundingbox)])
            self.light = (
                (self.boundingbox[1][1] - self.boundingbox[0][1]) * 2,
                (self.boundingbox[1][1] - self.boundingbox[0][1]) * 5,
                (self.boundingbox[1][1] - self.boundingbox[0][1]) * 2
            )

            if not self.normals:
                counter = 0
                while counter < len(self.vertices):
                    self.normals.append([0, 0, 0])
                    counter += 1
                for face in self.faces:
                    # print(face.split())
                    # print(self.vertices)
                    # input()
                    n_p1 = int(float(face.split()[0])) - 1
                    n_p2 = int(float(face.split()[1])) - 1
                    n_p3 = int(float(face.split()[2])) - 1
                    p1 = self.vertices[n_p1]
                    p2 = self.vertices[n_p2]
                    p3 = self.vertices[n_p3]

                    c1 = np.subtract(p2, p1)
                    c2 = np.subtract(p3, p1)
                    cross_result = np.cross(c1, c2)
                    self.normals[n_p1] = np.add(
                        self.normals[n_p1], cross_result).tolist()
                    self.normals[n_p2] = np.add(
                        self.normals[n_p2], cross_result).tolist()
                    self.normals[n_p2] = np.add(
                        self.normals[n_p3], cross_result).tolist()

            for face in self.faces:
                print("face", face)
                for points in face.split():
                    print("points", points)
                    if '/' in points:
                        # print(points)
                        # input()
                        vertex = tuple(points.split('//'))
                        v = int(vertex[0]) - 1
                        vn = int(vertex[-1]) - 1
                        self.data.append(self.vertices[v] + self.normals[vn])
                    else:
                        # print(points)
                        # input()
                        vn = int(points) - 1
                        self.data.append(self.vertices[vn] + normals[vn])
            glScale(self.scale, self.scale, self.scale)
            glTranslate(-self.center[0], -self.center[1], -self.center[2])

        else:
            sys.exit()

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
