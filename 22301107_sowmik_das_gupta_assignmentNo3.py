from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Camera and world variables
camera_pos = [0, 800, 400]
fovY = 120
GRID_LENGTH = 600

# Player state variables
player_x = 0
player_z = 0
player_angle = 90  # Start facing "up" the grid
player_life = 5
missed_bullets = 0
score = 0
game_over = False

# Game object lists
bullets = []
bullet_speed = 10
enemies = []
NUM_ENEMIES = 5

# Game state flags
cheat_mode = False
first_person_mode = False
cheat_vision_mode = False

# Animation variables
enemy_scale = 1.0
enemy_is_growing = True

# Cheat mode fire rate control
CHEAT_FIRE_RATE = 10  # Fire every 10 frames
cheat_fire_cooldown = 0

def new_enemy():
    """Generates a new enemy at a random position along the grid boundaries."""
    side = random.randint(0, 3)
    if side == 0:  # Top edge
        return {"x": random.uniform(-GRID_LENGTH, GRID_LENGTH), "z": GRID_LENGTH, "alive": True}
    elif side == 1:  # Bottom edge
        return {"x": random.uniform(-GRID_LENGTH, GRID_LENGTH), "z": -GRID_LENGTH, "alive": True}
    elif side == 2:  # Left edge
        return {"x": -GRID_LENGTH, "z": random.uniform(-GRID_LENGTH, GRID_LENGTH), "alive": True}
    else:  # Right edge
        return {"x": GRID_LENGTH, "z": random.uniform(-GRID_LENGTH, GRID_LENGTH), "alive": True}

def reset_game():
    """Resets all game variables to their initial states."""
    global player_x, player_z, player_angle, player_life, missed_bullets, score, game_over
    global cheat_mode, first_person_mode, cheat_vision_mode, enemy_scale, enemy_is_growing
    global bullets, enemies, cheat_fire_cooldown

    player_x, player_z, player_angle = 0, 0, 90
    player_life, missed_bullets, score = 5, 0, 0
    game_over = False
    cheat_mode, first_person_mode, cheat_vision_mode = False, False, False
    enemy_scale, enemy_is_growing = 1.0, True
    cheat_fire_cooldown = 0

    bullets.clear()
    enemies.clear()
    for _ in range(NUM_ENEMIES):
        enemies.append(new_enemy())

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen in a 2D overlay."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 800, 0)  # Flipped y-coordinates for proper text orientation
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid_and_walls():
    """Draws the checkerboard grid floor and the four surrounding walls."""
    # Draw Grid
    step = 100
    glBegin(GL_QUADS)
    for i in range(-GRID_LENGTH, GRID_LENGTH, step):
        for j in range(-GRID_LENGTH, GRID_LENGTH, step):
            if ((i + j) // step) % 2 == 0:
                glColor3f(1, 1, 1)  # White
            else:
                glColor3f(0.8, 0.7, 1.0) # Purple
            glVertex3f(i, j, 0)
            glVertex3f(i + step, j, 0)
            glVertex3f(i + step, j + step, 0)
            glVertex3f(i, j + step, 0)
    glEnd()

    # Draw Walls
    wall_height = 150
    glBegin(GL_QUADS)
    glColor3f(0, 0, 1)  # Blue Wall
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)

    glColor3f(0, 1, 1)  # Cyan Wall
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)

    glColor3f(0, 1, 0)  # Green Wall
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)

    glColor3f(255,255,255) # whitw wall
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

def draw_player():
    """Draws the player character using primitive shapes according to lab specifications."""
    glPushMatrix()
    glTranslatef(player_x, player_z, 50)
    glRotatef(player_angle, 0, 0, 1)
    
    # If game over, rotate player to lie down
    if game_over:
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -30)

    # Draw legs (blue cylinders)
    glColor3f(0, 0, 1)  # Royal Blue
    # Left leg cylinder
    glPushMatrix()
    glTranslatef(-15, 0, 0)
    gluCylinder(gluNewQuadric(), 12, 12, 50, 10, 10)
    glPopMatrix()
    
    # Right leg cylinder
    glPushMatrix()
    glTranslatef(15, 0, 0)
    gluCylinder(gluNewQuadric(), 12, 12, 50, 10, 10)
    glPopMatrix()
    
    # Draw torso (olive green cuboid)
    glColor3f(0.5, 0.5, 0)  # Olive Green
    glPushMatrix()
    glTranslatef(0, 0, 50)  # Above legs
    glScalef(40, 20, 50)  # width, depth, height
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw head (black sphere)
    glColor3f(0, 0, 0)  # Black
    glPushMatrix()
    glTranslatef(0, 0, 85)  # Top of torso
    glutSolidSphere(15, 16, 16)
    glPopMatrix()
    
    # Draw shoulders and hands (flesh color)
    glColor3f(0.96, 0.87, 0.70)  # Flesh tone
    
    # Shoulder spheres
    glPushMatrix()
    glTranslatef(-20, 0, 75)  # Left shoulder
    glutSolidSphere(8, 16, 16)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(20, 0, 75)  # Right shoulder
    glutSolidSphere(8, 16, 16)
    glPopMatrix()
    
    # Arms (cylinders from shoulders to hands)
    glPushMatrix()
    glTranslatef(-20, 0, 75)  # Left arm
    glRotatef(45, 1, 0, 0)  # Angle forward
    gluCylinder(gluNewQuadric(), 5, 5, 35, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(20, 0, 75)  # Right arm
    glRotatef(45, 1, 0, 0)  # Angle forward
    gluCylinder(gluNewQuadric(), 5, 5, 35, 10, 10)
    glPopMatrix()
    
    # Hand spheres
    glPushMatrix()
    glTranslatef(-20, 25, 55)  # Left hand
    glutSolidSphere(6, 16, 16)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(20, 25, 55)  # Right hand
    glutSolidSphere(6, 16, 16)
    glPopMatrix()
    
    # Draw gun (gray)
    glColor3f(0.7, 0.7, 0.7)  # Gray
    glPushMatrix()
    glTranslatef(0, 25, 55)  # Between hands
    
    # Main gun body
    glPushMatrix()
    glScalef(6, 35, 4)  # width, length, height
    glutSolidCube(1)
    glPopMatrix()
    
    # Gun grip
    glPushMatrix()
    glTranslatef(0, -5, -8)  # Below main body
    glScalef(4, 6, 12)  # width, depth, height
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()
    
    glPopMatrix()

def draw_enemy(enemy):
    """Draws an enemy, applying the scaling animation."""
    glPushMatrix()
    glTranslatef(enemy["x"], enemy["z"], 20)
    glScalef(enemy_scale, enemy_scale, enemy_scale) # Apply animation scale
    
    # Main Body
    glColor3f(1, 0, 0) # Red
    glutSolidSphere(20, 20, 20)
    
    # Eye
    glColor3f(0, 0, 0) # Black
    glTranslatef(0, 0, 15) # Position on top
    glutSolidSphere(10, 10, 10)
    
    glPopMatrix()

def draw_bullet(bullet):
    """Draws a single bullet."""
    glPushMatrix()
    glTranslatef(bullet["x"], bullet["z"], 50)
    glColor3f(1,0,0) # Yellow
    glutSolidCube(10)
    glPopMatrix()

def find_closest_enemy():
    """Finds the closest living enemy to the player."""
    closest_enemy = None
    min_dist = float('inf')
    for enemy in enemies:
        if enemy["alive"]:
            dist = math.sqrt((enemy["x"] - player_x)**2 + (enemy["z"] - player_z)**2)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
    return closest_enemy

def update_game_state():
    """Handles all game logic updates per frame."""
    global missed_bullets, score, game_over, player_life, player_angle
    global enemy_scale, enemy_is_growing, cheat_fire_cooldown

    # Animate enemy size
    if enemy_is_growing:
        enemy_scale += 0.015
        if enemy_scale > 1.4: enemy_is_growing = False
    else:
        enemy_scale -= 0.015
        if enemy_scale < 0.8: enemy_is_growing = True

    # Decrement cheat fire cooldown
    if cheat_fire_cooldown > 0:
        cheat_fire_cooldown -= 1

    if game_over:
        bullets.clear()
        enemies.clear()
        return

    # Handle cheat mode logic
    if cheat_mode:
        target = find_closest_enemy()
        if target:
            dx = target["x"] - player_x
            dz = target["z"] - player_z
            target_angle = math.degrees(math.atan2(dz, dx))
            
            # Normalize angles to handle wrapping
            angle_diff = (target_angle - player_angle + 180) % 360 - 180
            
            # Rotate towards the target
            if abs(angle_diff) > 4: # Rotation speed
                player_angle += 4 if angle_diff > 0 else -4
            else: # If facing the enemy, fire
                player_angle = target_angle
                if cheat_fire_cooldown == 0:
                    fire_bullet()
                    cheat_fire_cooldown = CHEAT_FIRE_RATE
        else: # If no enemies, just spin
            player_angle = (player_angle + 4) % 360

    # Update bullet positions and check for collisions
    active_bullets = []
    for b in bullets:
        b["x"] += b["dx"] * bullet_speed
        b["z"] += b["dz"] * bullet_speed
        
        hit_enemy = False
        # Bullet-Enemy collision
        for i, e in enumerate(enemies):
            if e["alive"]:
                dist = math.sqrt((b["x"] - e["x"])**2 + (b["z"] - e["z"])**2)
                if dist < 30: # Collision radius
                    score += 1
                    hit_enemy = True
                    enemies[i] = new_enemy()
                    break
        
        # Check if bullet is out of bounds or hit an enemy
        if not hit_enemy and abs(b["x"]) < GRID_LENGTH and abs(b["z"]) < GRID_LENGTH:
            active_bullets.append(b)
        elif not hit_enemy:
            missed_bullets += 1
            
    bullets[:] = active_bullets

    # Update enemy positions and check for player collision
    for i, e in enumerate(enemies):
        if e["alive"]:
            dx = player_x - e["x"]
            dz = player_z - e["z"]
            dist = math.sqrt(dx**2 + dz**2) + 1e-9 # Avoid division by zero
            
            # Move enemy towards player
            e["x"] += dx / dist * 0.02  # 0.02 pixels per second movement speed
            e["z"] += dz / dist * 0.02

            # Player-Enemy collision
            if dist < 40:
                player_life -= 1
                enemies[i] = new_enemy()

    # Check for game over conditions
    if player_life <= 0 or missed_bullets >= 10:
        game_over = True

def fire_bullet():
    """Creates a new bullet based on the player's current position and angle."""
    if game_over: return
    angle_rad = math.radians(player_angle)
    dx = math.cos(angle_rad)
    dz = math.sin(angle_rad)
    
    # Spawn bullet at the tip of the gun
    gun_offset = 40
    spawn_x = player_x + dx * gun_offset
    spawn_z = player_z + dz * gun_offset
    
    bullets.append({"x": spawn_x, "z": spawn_z, "dx": dx, "dz": dz})

def keyboardListener(key, x, y):
    """Handles standard key presses."""
    global player_x, player_z, player_angle, cheat_mode, cheat_vision_mode
    
    if game_over:
        if key == b'r': reset_game()
        return

    move_speed = 20 # Player speed
    angle_rad = math.radians(player_angle)
    
    if key == b'w':
        player_x += math.cos(angle_rad) * move_speed
        player_z += math.sin(angle_rad) * move_speed
    elif key == b's':
        player_x -= math.cos(angle_rad) * move_speed
        player_z -= math.sin(angle_rad) * move_speed
    
    # Clamp player position to stay within bounds
    player_x = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_x))
    player_z = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_z))

    if not cheat_mode:
        if key == b'a': player_angle += 5
        if key == b'd': player_angle -= 5
    
    if key == b'c': cheat_mode = not cheat_mode
    if key == b'v': cheat_vision_mode = not cheat_vision_mode

def specialKeyListener(key, x, y):
    """Handles special key presses (arrow keys)."""
    global camera_pos
    if first_person_mode: return

    cx, cy, cz = camera_pos
    dist = math.sqrt(cx**2 + cy**2)
    angle = math.atan2(cy, cx)

    if key == GLUT_KEY_UP: cz += 20
    if key == GLUT_KEY_DOWN: cz -= 20
    if key == GLUT_KEY_LEFT: angle += 0.1
    if key == GLUT_KEY_RIGHT: angle -= 0.1
    
    cx = dist * math.cos(angle)
    cy = dist * math.sin(angle)
    camera_pos = [cx, cy, cz]

def mouseListener(button, state, x, y):
    """Handles mouse clicks."""
    global first_person_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not cheat_mode:
        fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode

def setupCamera():
    """Configures the camera projection and view."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person_mode:
        cam_angle = player_angle
        if cheat_mode and cheat_vision_mode:
            cam_angle = player_angle
        
        angle_rad = math.radians(cam_angle)
        cam_x = player_x - 150 * math.cos(angle_rad)
        cam_z = player_z - 150 * math.sin(angle_rad)
        gluLookAt(cam_x, cam_z, 100,
                  player_x, player_z, 70,
                  0, 0, 1)
    else:
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
                  0, 0, 0,
                  0, 0, 1)

def showScreen():
    """The main rendering function."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    draw_grid_and_walls()
    draw_player()
    
    if not game_over:
        # Draw all bullets
        for bullet in bullets:
            draw_bullet(bullet)
        
        # Draw all enemies
        for enemy in enemies:
            if enemy["alive"]:
                draw_enemy(enemy)
        
        # In-Game HUD
        draw_text(10, 770, f"Player Life Remaining: {player_life}")
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {missed_bullets}")
        if cheat_mode:
            draw_text(10, 680, "CHEAT MODE ACTIVE")
        if first_person_mode:
            draw_text(10, 650, "FIRST PERSON MODE")
    else:
        # Game Over HUD
        draw_text(350, 450, f"Game is Over. Your Score is {score}.")
        draw_text(350, 420, 'Press "R" to RESTART the Game.')
        
    glutSwapBuffers()

def idle():
    """The idle function, called continuously."""
    update_game_state()
    glutPostRedisplay()

def main():
    """Initializes GLUT and enters the main loop."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Bullet Frenzy")
    
    glEnable(GL_DEPTH_TEST)
    
    reset_game()
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
