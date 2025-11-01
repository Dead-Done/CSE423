from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
# import math

# Window dimensions
MY_WIN_WIDTH, MY_WIN_HEIGHT = 500, 500

#===============================================
# TASK 1: My Rainy Cottage
#===============================================

#Variables for rain and background
my_raindrops = []
rain_angle = 0
bg_brightness = 0.0

class MyRaindrop:
    """Represents a single raindrop in the scene."""
    def __init__(self):
        self.x = random.randint(-250, 250)
        self.y = 250
        self.fall_speed = random.uniform(2, 5)
        self.length = 10  #length of raindrop line

def my_convert_coords(x, y):
    """Convert screen coordinates to OpenGL world coordinates."""
    wx = x - (MY_WIN_WIDTH / 2)
    wy = (MY_WIN_HEIGHT / 2) - y
    return wx, wy

def my_draw_point(x, y, size): #for bouncing points
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def my_draw_line(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def my_draw_triangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

def draw_my_cottage():
    # Cottage base
    glColor3f(0.7, 0.5, 0.3)
    my_draw_triangle(-100, -50, -100, 50, 100, 50)
    my_draw_triangle(-100, -50, 100, 50, 100, -50)
    # Roof
    glColor3f(0.5, 0.2, 0.1)
    my_draw_triangle(-120, 50, 0, 120, 120, 50)
    # Door
    glColor3f(0.3, 0.15, 0.05)
    my_draw_triangle(-20, -50, -20, 10, 20, 10)
    my_draw_triangle(-20, -50, 20, 10, 20, -50)
    # Windows
    glColor3f(0.2, 0.4, 0.7)
    my_draw_triangle(-80, 0, -80, 30, -50, 30)
    my_draw_triangle(-80, 0, -50, 30, -50, 0)
    my_draw_triangle(50, 0, 50, 30, 80, 30)
    my_draw_triangle(50, 0, 80, 30, 80, 0)

def update_my_raindrops():
    global my_raindrops, rain_angle
    for drop in my_raindrops:
        drop.y -= drop.fall_speed
        drop.x += rain_angle
        if drop.y < -250:
            drop.y = 250
            drop.x = random.randint(-250, 250)

def draw_my_raindrops():
    glColor3f(0.5, 0.7, 1.0)  #slightly brighter blue color
    for drop in my_raindrops:
        # Draw rain as short diagonal lines
        my_draw_line(
            drop.x, drop.y,  # Start of line
            drop.x + rain_angle * 2, drop.y - drop.length  # End of line
        )

def my_cottage_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(bg_brightness, bg_brightness, bg_brightness, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    draw_my_cottage()
    draw_my_raindrops()
    glutSwapBuffers()

def my_cottage_keyboard(key, x, y):
    global rain_angle, bg_brightness
    if key == b'n':  # Night mode
        bg_brightness = 0.0
    if key == b'd':  # Day mode
        bg_brightness = 0.8
    glutPostRedisplay()

def my_cottage_special_keys(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT:
        rain_angle -= 0.2
    if key == GLUT_KEY_RIGHT:
        rain_angle += 0.2
    glutPostRedisplay()

def my_cottage_animate():
    update_my_raindrops()
    glutPostRedisplay()

def my_cottage_init():
    global my_raindrops
    for i in range(100):
        drop = MyRaindrop()
        my_raindrops.append(drop)
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

def run_my_cottage():
    glutInit()
    glutInitWindowSize(MY_WIN_WIDTH, MY_WIN_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"My Rainy Cottage")
    my_cottage_init()
    glutDisplayFunc(my_cottage_display)
    glutIdleFunc(my_cottage_animate)
    glutKeyboardFunc(my_cottage_keyboard)
    glutSpecialFunc(my_cottage_special_keys)
    glutMainLoop()

#===============================================
# TASK 2: Colorful Bouncing Box
#===============================================

# Variables for moving points
bouncer_points = []
bouncer_speed = 1.0
blink_on = False
frozen = False
blink_tick = 0

class BouncerPoint:
    """Represents a moving colored point inside the box."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        self.r = random.uniform(0.2, 1.0)
        self.g = random.uniform(0.2, 1.0)
        self.b = random.uniform(0.2, 1.0)
        self.visible = True

def update_bouncer_points():
    global bouncer_points, bouncer_speed, frozen
    if frozen:
        return
    for pt in bouncer_points:
        pt.x += pt.dx * bouncer_speed
        pt.y += pt.dy * bouncer_speed
        if pt.x > 200 or pt.x < -200:
            pt.dx = -pt.dx
        if pt.y > 200 or pt.y < -200:
            pt.dy = -pt.dy

def draw_bouncer_points():
    global blink_on, blink_tick
    for pt in bouncer_points:
        if blink_on:
            if blink_tick % 60 < 30:
                glColor3f(pt.r, pt.g, pt.b)
            else:
                glColor3f(0.0, 0.0, 0.0)
        else:
            glColor3f(pt.r, pt.g, pt.b)
        my_draw_point(pt.x, pt.y, 5)

def draw_bouncer_box():
    glColor3f(1.0, 1.0, 1.0)
    my_draw_line(-200, -200, 200, -200)
    my_draw_line(200, -200, 200, 200)
    my_draw_line(200, 200, -200, 200)
    my_draw_line(-200, 200, -200, -200)

def bouncer_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    draw_bouncer_box()
    draw_bouncer_points()
    glutSwapBuffers()

def bouncer_keyboard(key, x, y):
    global bouncer_speed, blink_on, frozen
    if key == b' ':
        frozen = not frozen
    glutPostRedisplay()

def bouncer_special_keys(key, x, y):
    global bouncer_speed
    if key == GLUT_KEY_UP:
        bouncer_speed *= 1.2
    if key == GLUT_KEY_DOWN:
        bouncer_speed /= 1.2
    glutPostRedisplay()

def bouncer_mouse(button, state, x, y):
    global bouncer_points, blink_on
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        px, py = my_convert_coords(x, y)
        if -200 <= px <= 200 and -200 <= py <= 200:
            new_pt = BouncerPoint(px, py)
            bouncer_points.append(new_pt)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blink_on = not blink_on
    glutPostRedisplay()

def bouncer_animate():
    global blink_tick
    update_bouncer_points()
    blink_tick += 1
    glutPostRedisplay()

def bouncer_init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

def run_bouncer_box():
    glutInit()
    glutInitWindowSize(MY_WIN_WIDTH, MY_WIN_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"Colorful Bouncing Box")
    bouncer_init()
    glutDisplayFunc(bouncer_display)
    glutIdleFunc(bouncer_animate)
    glutKeyboardFunc(bouncer_keyboard)
    glutSpecialFunc(bouncer_special_keys)
    glutMouseFunc(bouncer_mouse)
    glutMainLoop()

#===============================================
# Program Selector
#===============================================

if __name__ == "__main__":
    print("CSE423 Lab Assignment 1 - Personalized Edition")
    print("Choose which creative task to run:")
    print("1. My Rainy Cottage")
    print("2. Colorful Bouncing Box")
    user_choice = input("Enter choice (1 or 2): ")
    if user_choice == "1":
        print("\nLaunching Task 1...")
        print("Controls:")
        print("- Left/Right arrows: Bend rain direction")
        print("- 'n' key: Night mode")
        print("- 'd' key: Day mode")
        run_my_cottage()
    elif user_choice == "2":
        print("\nLaunching Task 2...")
        print("Controls:")
        print("- Right click: Add bouncing points")
        print("- Left click: Toggle blink effect")
        print("- Up/Down arrows: Adjust speed")
        print("- Spacebar: Freeze/Resume movement")
        run_bouncer_box()
    else:
        print("Invalid choice! Please run again and choose 1 or 2.")