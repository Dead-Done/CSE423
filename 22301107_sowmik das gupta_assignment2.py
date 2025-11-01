from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

W_Width, W_Height = 500, 500

#variables for game
catcher_x = 0
catcher_y = -200
catcher_width = 80
catcher_height = 20
catcher_color = [1.0, 1.0, 1.0] #white color

diamond_x = 0
diamond_y = 200
diamond_size = 15
diamond_color = [1.0, 1.0, 1.0] #white initially
diamond_speed = 0.2 #how fast diamond falls

score = 0
game_over = False
game_paused = False
last_time = time.time() #for timing

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    #checking which zone the line is in
    if abs(dx) >= abs(dy):
        if dx > 0 and dy >= 0:
            return 0 #zone 0
        elif dx <= 0 and dy > 0:
            return 3 #zone 3
        elif dx < 0 and dy <= 0:
            return 4 #zone 4
        elif dx >= 0 and dy < 0:
            return 7 #zone 7
    else:
        if dx > 0 and dy > 0:
            return 1 #zone 1
        elif dx <= 0 and dy > 0:
            return 2 #zone 2
        elif dx < 0 and dy < 0:
            return 5 #zone 5
        elif dx >= 0 and dy < 0:
            return 6 #zone 6

def convert_to_zone0(x, y, zone):
    #converting points from any zone to zone 0
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def convert_from_zone0(x, y, zone):
    #converting back from zone 0 to original zone
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def midpoint_line(x1, y1, x2, y2):
    #main midpoint line algorithm
    zone = find_zone(x1, y1, x2, y2)
    
    #convert to zone 0
    x1_new, y1_new = convert_to_zone0(x1, y1, zone)
    x2_new, y2_new = convert_to_zone0(x2, y2, zone)
    
    #make sure x1 is smaller than x2
    if x1_new > x2_new:
        x1_new, x2_new = x2_new, x1_new
        y1_new, y2_new = y2_new, y1_new
    
    #calculating d and increments
    dx = x2_new - x1_new
    dy = y2_new - y1_new
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    
    x = x1_new
    y = y1_new
    
    points = [] #list to store all points
    
    #midpoint algorithm loop
    while x <= x2_new:
        orig_x, orig_y = convert_from_zone0(x, y, zone)
        points.append((orig_x, orig_y))
        
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE
        x = x + 1
    
    return points

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_line_with_points(x1, y1, x2, y2):
    #draws line using midpoint algorithm
    points = midpoint_line(int(x1), int(y1), int(x2), int(y2))
    for point in points:
        draw_pixel(point[0], point[1])

def draw_diamond(x, y, size):
    glColor3f(diamond_color[0], diamond_color[1], diamond_color[2])
    
    #drawing diamond with 4 lines
    draw_line_with_points(x, y + size, x + size, y) #top to right
    draw_line_with_points(x + size, y, x, y - size) #right to bottom
    draw_line_with_points(x, y - size, x - size, y) #bottom to left
    draw_line_with_points(x - size, y, x, y + size) #left to top

def draw_catcher(x, y, width, height):
    glColor3f(catcher_color[0], catcher_color[1], catcher_color[2])
    
    #drawing catcher bowl shape
    draw_line_with_points(x - width//2, y, x - width//2, y + height) #left side
    draw_line_with_points(x - width//2, y + height, x + width//2, y + height) #top
    draw_line_with_points(x + width//2, y + height, x + width//2, y) #right side
    draw_line_with_points(x + width//2, y, x - width//2, y) #bottom

def draw_restart_button():
    glColor3f(0.0, 1.0, 1.0)  #teal color
    #making left arrow shape for restart
    draw_line_with_points(-220, 220, -200, 240)
    draw_line_with_points(-200, 240, -200, 230)
    draw_line_with_points(-200, 230, -180, 230)
    draw_line_with_points(-180, 230, -180, 210)
    draw_line_with_points(-180, 210, -200, 210)
    draw_line_with_points(-200, 210, -200, 200)
    draw_line_with_points(-200, 200, -220, 220)

def draw_pause_play_button():
    glColor3f(1.0, 0.6, 0.0)  #amber color
    if game_paused:
        #making play button (triangle shape)
        draw_line_with_points(-20, 240, 0, 225)
        draw_line_with_points(0, 225, -20, 210)
        draw_line_with_points(-20, 210, -20, 240)
    else:
        #making pause button (two lines)
        draw_line_with_points(-25, 240, -25, 210)
        draw_line_with_points(-15, 240, -15, 210)

def draw_exit_button():
    glColor3f(1.0, 0.0, 0.0)  #red color
    #making cross/X shape
    draw_line_with_points(180, 240, 220, 200)
    draw_line_with_points(220, 240, 180, 200)

def check_collision():
    #checking if diamond and catcher are touching
    if (abs(diamond_x - catcher_x) < (diamond_size + catcher_width//2) and
        abs(diamond_y - catcher_y) < (diamond_size + catcher_height//2)):
        return True
    return False

def reset_diamond():
    #making new diamond at random position
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(-200, 200)
    diamond_y = 200
    diamond_color = [random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0)]

def restart_game():
    #resetting everything to start again
    global score, game_over, diamond_speed, catcher_color
    score = 0
    game_over = False
    diamond_speed = 0.2
    catcher_color = [1.0, 1.0, 1.0] #white again
    reset_diamond()
    print("Starting Over")

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0) #black background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    
    #drawing all the buttons
    draw_restart_button()
    draw_pause_play_button()
    draw_exit_button()
    
    #drawing game stuff
    if not game_over:
        draw_diamond(diamond_x, diamond_y, diamond_size)
    draw_catcher(catcher_x, catcher_y, catcher_width, catcher_height)
    
    glutSwapBuffers()

def update():
    #main game update function
    global diamond_y, score, game_over, diamond_speed, catcher_color, last_time
    
    if game_over or game_paused:
        return #dont update if game stopped
    
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    diamond_y -= diamond_speed #move diamond down
    
    #check if caught diamond
    if check_collision():
        score += 1
        print(f"Score: {score}")
        diamond_speed += 0.1  #make it faster
        reset_diamond()
    
    #check if diamond fell down
    elif diamond_y < -250:
        game_over = True
        catcher_color = [1.0, 0.0, 0.0]  #turn red when game over
        print(f"Game Over! Final Score: {score}")
    
    glutPostRedisplay()

def keyboard(key, x, y):
    global catcher_x
    
    if game_over or game_paused:
        return #cant move when game is over or paused
    
    #moving catcher left and right
    if key == b'a' and catcher_x > -220:
        catcher_x -= 25
    elif key == b'd' and catcher_x < 220:
        catcher_x += 25
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global catcher_x
    
    if game_over or game_paused:
        return
    
    #arrow keys for moving catcher
    if key == GLUT_KEY_LEFT and catcher_x > -220:
        catcher_x -= 25
    elif key == GLUT_KEY_RIGHT and catcher_x < 220:
        catcher_x += 25
    
    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global game_paused
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        #converting mouse position to our coordinate system
        mouse_x = x - W_Width//2
        mouse_y = W_Height//2 - y
        
        #checking which button was clicked
        if -220 <= mouse_x <= -180 and 200 <= mouse_y <= 240: #restart button
            restart_game()
        
        elif -30 <= mouse_x <= 10 and 200 <= mouse_y <= 240: #pause/play button
            game_paused = not game_paused
            if game_paused:
                print("Game Paused")
            else:
                print("Game Resumed")
        
        elif 180 <= mouse_x <= 220 and 200 <= mouse_y <= 240: #exit button
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop() #close game
    
    glutPostRedisplay()

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)
    glPointSize(2) #making points bigger so lines are visible
    reset_diamond() #start with first diamond

if __name__ == "__main__":
    print("CSE423 Assignment 2: Catch the Diamonds!")
    print("Controls:")
    print("- Left/Right arrows or A/D keys: Move catcher")
    print("- Click restart button (teal arrow): Restart game")
    print("- Click pause/play button (amber): Pause/resume")
    print("- Click exit button (red cross): Exit game")
    
    glutInit()
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
    
    wind = glutCreateWindow(b"Catch the Diamonds!")
    init()
    
    #setting up all the callback functions
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click)
    
    glutMainLoop() #start the game loop