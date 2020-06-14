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
        self.width = width
        self.height = height
        self.vertices = []
        self.faces = []
        self.normals = []
        self.data = []
        self.boundingbox = []
        self.center = []
        self.scale = []
        self.myvbo = []
        self.light = (0.0, 0.0, 0.0)
        self.shadow = False
        self.backgroundCol = (1.0, 1.0, 1.0, 1.0)
        self.objectCol = (0.05, 0.6, 1.0, 1.0)

    # read Object from File
    def readObject(self):
        if len(sys.argv) == 2:
            f = open(sys.argv[1])
            lines = f.readlines()
            for line in lines:
                if line:
                    if line.startswith('f'):  # Polygone
                        self.faces.append(line.split()[1:])
                    elif line.startswith('vn'):  # Vertex-Normalen
                        self.normals.append(
                            [float(vn) for vn in line.split()[1:]])
                    elif line.startswith('v'):  # Objekt-Punkte
                        self.vertices.append(
                            [float(v) for v in line.split()[1:]])

            self.boundingbox = [list(map(min, zip(*self.vertices))),
                                list(map(max, zip(*self.vertices)))]
            self.center = [(x[0] + x[1]) / 2.0 for x in zip(*self.boundingbox)]
            self.scale = 0.75 / max([x[1] - x[0]
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
                    # print(face.split("//"))
                    # print(face)
                    # # print(self.vertices)
                    # input()
                    n_p1 = int(float(face[0])) - 1
                    n_p2 = int(float(face[1])) - 1
                    n_p3 = int(float(face[2])) - 1
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
                # print("face", face)
                for points in face:
                    # print("points", points)
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
                        self.data.append(self.vertices[vn] + self.normals[vn])
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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(self.backgroundCol[0], self.backgroundCol[1],
                     self.backgroundCol[2], self.backgroundCol[3])
        glColor3f(self.objectCol[0], self.objectCol[1], self.objectCol[2])
        self.myvbo = vbo.VBO(np.array(self.data, 'f'))
        self.myvbo.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnable(GL_COLOR_MATERIAL)
        glVertexPointer(3, GL_FLOAT, 24, self.myvbo)
        glNormalPointer(GL_FLOAT, 24, self.myvbo + 12)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if self.shadow:
            p = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0 /
                 self.light[1], 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            glPushMatrix()
            glColor(0.0, 0.0, 0.0, 0.0)
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)

            glTranslatef(self.light[0], self.light[1], self.light[2])
            glTranslatef(0.0, self.boundingbox[0][1], 0.0)
            glMultMatrixf(p)
            glTranslatef(0.0, -self.boundingbox[0][1], 0.0)
            glTranslatef(-self.light[0], -self.light[1], -self.light[2])
            glDrawArrays(GL_TRIANGLES, 0, len(self.data))

            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()

        glColor3f(self.objectCol[0],
                  self.objectCol[1], self.objectCol[2])
        glDrawArrays(GL_TRIANGLES, 0, len(self.data))

        self.myvbo.unbind()
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glFlush()
