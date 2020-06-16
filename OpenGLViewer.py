import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np
import math

from Scene import Scene


class OpenGLViewer:
    """GLFW Rendering window class"""

    def __init__(self):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = 640, 480
        self.aspectwidth = float(self.width) / self.height
        self.aspectheight = float(self.height) / self.width
        self.window = glfw.create_window(
            self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glOrtho(
            -1.5 * self.width / self.height, 1.5 *
            self.width / self.height, -1.5, 1.5, -1.0, 1.0
        )
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMove)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.preventDistort)

        # create 3D
        self.scene = Scene(self.width, self.height)

        # exit flag
        self.exitNow = False

        # animation flag
        self.animation = True

        # mouse
        self.middleMouseClicked = False
        self.leftMouseClicked = False
        self.rightMouseClicked = False
        self.lastY = 0
        self.orthoP = True
        self.perspP = False

    def preventDistort(self, win, width, height):
        self.width = width
        self.height = height

        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.orthoP:
            self.changeOrthoP(self.width, self.height)
        if self.perspP:
            self.changePerspP(self.width, self.height)

        glMatrixMode(GL_MODELVIEW)

    def projectOnSphere(self, x, y, r):
        x, y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y ** 2)
        z = np.sqrt(r * r - a)
        l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        return x / l, y / l, z / l

    def onMouseButton(self, win, button, action, mods):
        r = min(self.width, self.height) / 2.0
        print("mouse button: ", win, button, action, mods)
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self.middleMouseClicked = True
            elif action == glfw.RELEASE:
                self.middleMouseClicked = False

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.leftMouseClicked = True
                self.scene.startP = self.scene.projectOnSphere(
                    self.scene.mousePosX, self.scene.mousePosY, r)
            elif action == glfw.RELEASE:
                self.leftMouseClicked = False
                self.scene.actOri = self.scene.actOri * self.scene.rotate(
                    self.scene.angle, self.scene.axis)
                self.scene.angle = 0

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.rightMouseClicked = True
            elif action == glfw.RELEASE:
                self.rightMouseClicked = False

    def onMouseMove(self, win, posX, posY):
        r = min(self.width, self.height) / 2.0
        self.scene.mousePosX = posX
        self.scene.mousePosY = posY

        if self.middleMouseClicked:
            y = posY - self.scene.startZP[1]
            if self.lastY - y > 0:
                glScale(0.95, 0.95, 0.95)
            else:
                glScale(1.05, 1.05, 1.05)
            self.lastY = y

        if self.leftMouseClicked:
            moveP = self.scene.projectOnSphere(posX, posY, r)
            self.scene.angle = math.acos(np.dot(self.scene.startP, moveP))
            self.scene.axis = np.cross(self.scene.startP, moveP)
            # glMultMatrixf(self.scene.actOri *
            #               self.scene.rotate(self.scene.angle, self.scene.axis))
            glRotatef(2.5, self.scene.axis[0],
                      self.scene.axis[1], self.scene.axis[2])

        if self.rightMouseClicked:
            x = posX - self.scene.startMP[0]
            y = -(posY - self.scene.startMP[1])
            glTranslate(x/self.width, y/self.height, 0)

        self.scene.startMP = (posX, posY)
        self.scene.startP = self.scene.projectOnSphere(posX, posY, r)

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_V:
                # toggle show vector
                self.scene.showVector = not self.scene.showVector
            if key == glfw.KEY_A:
                # toggle animation
                self.animation = not self.animation

            # Change Color to Default
            if key == glfw.KEY_D:
                self.scene.backgroundCol = (1.0, 1.0, 1.0, 0.0)
                self.scene.objectCol = (0.05, 0.6, 1.0, 1.0)

            # Change Color to Black
            if key == glfw.KEY_S and not mods == glfw.MOD_SHIFT:
                self.scene.backgroundCol = (0.0, 0.0, 0.0, 0.0)
            if key == glfw.KEY_S and mods == glfw.MOD_SHIFT:
                self.scene.objectCol = (0.0, 0.0, 0.0, 0.0)

            # Change Color to White
            if key == glfw.KEY_W and not mods == glfw.MOD_SHIFT:
                self.scene.backgroundCol = (1.0, 1.0, 1.0, 0.0)
            if key == glfw.KEY_W and mods == glfw.MOD_SHIFT:
                self.scene.objectCol = (1.0, 1.0, 1.0, 0.0)

            # Change Color to Red
            if key == glfw.KEY_R and not mods == glfw.MOD_SHIFT:
                self.scene.backgroundCol = (1.0, 0.0, 0.0, 0.0)
            if key == glfw.KEY_R and mods == glfw.MOD_SHIFT:
                self.scene.objectCol = (1.0, 0.0, 0.0, 0.0)

            # Change Color to Yellow
            if key == glfw.KEY_G and not mods == glfw.MOD_SHIFT:
                self.scene.backgroundCol = (1.0, 1.0, 0.0, 0.0)
            if key == glfw.KEY_G and mods == glfw.MOD_SHIFT:
                self.scene.objectCol = (1.0, 1.0, 0.0, 0.0)

            # Change Color to Blue
            if key == glfw.KEY_B and not mods == glfw.MOD_SHIFT:
                self.scene.backgroundCol = (0.0, 0.0, 1.0, 0.0)
            if key == glfw.KEY_B and mods == glfw.MOD_SHIFT:
                self.scene.objectCol = (0.0, 0.0, 1.0, 0.0)

            # Enable/Disable Shadow
            if key == glfw.KEY_H:
                if self.scene.shadow == False:
                    self.scene.shadow = True
                else:
                    self.scene.shadow = False

            # Enable Orthogonal Projection
            if key == glfw.KEY_O:
                if self.orthoP == False:
                    self.orthoP = True
                    self.perspP = False
                    self.preventDistort(win, self.width, self.height)

            # Enable Perspective Projection
            if key == glfw.KEY_P:
                if self.perspP == False:
                    self.perspP = True
                    self.orthoP = False
                    self.preventDistort(win, self.width, self.height)

    def changeOrthoP(self, width, height):
        if self.orthoP:
            self.aspectwidth = float(self.width) / self.height
            self.aspectheight = float(self.height) / self.width
            if width <= height:
                glOrtho(-1.5, 1.5, -1.5 * self.aspectheight,
                        1.5 * self.aspectheight, -1.0, 1.0)
            else:
                glOrtho(-1.5 * self.aspectwidth, 1.5 *
                        self.aspectwidth, -1.5, 1.5, -1.0, 1.0)

    def changePerspP(self, width, height):
        if self.perspP:
            self.aspectwidth = float(self.width) / self.height
            self.aspectheight = float(self.height) / self.width
            if width <= height:
                glFrustum(-1.0, 1.0, -1.0 * self.aspectheight,
                          1.0 * self.aspectheight, 1.5, 25)
            else:
                glFrustum(-1.0*self.aspectwidth, 1.0 *
                          self.aspectwidth, -1.0, 1.0, 1.5, 25)
            gluLookAt(0, 0, 3.5, 0, 0, 0, 0, 2, 0)

    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        self.scene.readObject()

        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0/self.frame_rate:
                # update time
                t = currT
                # clear
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # render scene
                self.scene.render()

                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()


# main() function
def main():
    print("Simple glfw render Window")
    rw = OpenGLViewer()
    rw.run()


# call main
if __name__ == '__main__':
    main()
