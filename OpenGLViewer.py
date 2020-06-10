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
        self.aspect = self.width/float(self.height)
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
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMove)

        # create 3D
        self.scene = Scene(self.width, self.height)

        # exit flag
        self.exitNow = False

        # animation flag
        self.animation = True

        # mouse
        self.startZoomPoint = (0, 0)
        self.middleMouseClicked = False
        self.lasty = 0

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self.middleMouseClicked = True
            elif action == glfw.RELEASE:
                self.middleMouseClicked = False
                # self.angle = 0
            print("heran- bzw. wegzoomen")

    def onMouseMove(self, win, posX, posY):
        r = min(self.width, self.height) / 2.0
        if self.middleMouseClicked:
            y = posY - self.startZoomPoint[1]
            if self.lasty - y > 0:
                glScale(0.9, 0.9, 0.9)
            else:
                glScale(1.1, 1.1, 1.1)
            self.lasty = y

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
                print("Schatten an/aus")

    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        self.width = width
        self.height = height
        self.aspect = width/float(height)
        glViewport(0, 0, self.width, self.height)

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
                if self.animation:
                    self.scene.step()
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
