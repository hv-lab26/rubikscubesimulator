import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit, glutSolidCube
import sys
import math

COLORS = {
    'W': (1.0, 1.0, 1.0),  # White
    'R': (1.0, 0.0, 0.0),  # Red
    'G': (0.0, 1.0, 0.0),  # Green  
    'O': (1.0, 0.5, 0.0),  # Orange
    'B': (0.0, 0.0, 1.0),  # Blue
    'Y': (1.0, 1.0, 0.0)   # Yellow
}

CUBIE_SIZE = 0.9
SPACING = 1.05

class SimpleCube:
    def __init__(self):
        self.cubies = []
        self.init_cube()
        self.is_animating = False
        self.animation_progress = 0.0
        self.animation_speed = 0.08
        self.current_rotation = None
    
    def init_cube(self):
        self.cubies = []
        
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    if x == 0 and y == 0 and z == 0:  
                        continue
                    
                    cubie = {
                        'pos': [x, y, z],
                        'colors': {}
                    }
                    
                    if x == 1:  cubie['colors']['right'] = 'R'
                    if x == -1: cubie['colors']['left'] = 'O'
                    if y == 1:  cubie['colors']['top'] = 'W'
                    if y == -1: cubie['colors']['bottom'] = 'Y'
                    if z == 1:  cubie['colors']['front'] = 'G'
                    if z == -1: cubie['colors']['back'] = 'B'
                    
                    self.cubies.append(cubie)
        
        print(f"Initialized {len(self.cubies)} cubies")
    
    def get_layer_cubies(self, axis, layer):
        indices = []
        for i, cubie in enumerate(self.cubies):
            x, y, z = cubie['pos']
            if axis == 'x' and x == layer:
                indices.append(i)
            elif axis == 'y' and y == layer:
                indices.append(i)
            elif axis == 'z' and z == layer:
                indices.append(i)
        return indices
    
    def rotate_layer(self, axis, layer, clockwise=True):
        if self.is_animating:
            return False
        
        angle = 90 if clockwise else -90
        self.current_rotation = {
            'axis': axis,
            'layer': layer,
            'angle': angle,
            'indices': self.get_layer_cubies(axis, layer)
        }
        self.is_animating = True
        self.animation_progress = 0.0
        return True
    
    def update_animation(self):
        if not self.is_animating:
            return
        
        self.animation_progress += self.animation_speed
        
        if self.animation_progress >= 1.0:
            self.complete_rotation()
            self.is_animating = False
            self.animation_progress = 0.0
            self.current_rotation = None
    
    def complete_rotation(self):
        if not self.current_rotation:
            return
        
        axis = self.current_rotation['axis']
        layer = self.current_rotation['layer']
        clockwise = self.current_rotation['angle'] > 0
        indices = self.current_rotation['indices']
        
        print(f"Completing {axis} rotation, layer={layer}, clockwise={clockwise}")
        
        old_data = []
        for i in indices:
            old_data.append({
                'pos': self.cubies[i]['pos'].copy(),
                'colors': self.cubies[i]['colors'].copy()
            })
        
        face_type = None
        color_clockwise = clockwise
        
        if axis == 'y':
            if layer == 1:
                face_type = 'U'  
                color_clockwise = clockwise
            else:  
                face_type = 'D' 
                color_clockwise = clockwise  
        elif axis == 'x':
            if layer == 1:
                face_type = 'R'  
                color_clockwise = not clockwise  
            else:  
                face_type = 'L'  
                color_clockwise = not clockwise  
        elif axis == 'z':
            if layer == 1:
                face_type = 'F'  
                color_clockwise = clockwise
            else:  
                face_type = 'B'  
                color_clockwise = clockwise  
        
        print(f"Face type: {face_type}, Color rotation clockwise: {color_clockwise}")
        
        for idx, i in enumerate(indices):
            new_pos = self.rotate_position(old_data[idx]['pos'], axis, clockwise)
            new_colors = self.rotate_colors(old_data[idx]['colors'], axis, color_clockwise)
            
            self.cubies[i]['pos'] = new_pos
            self.cubies[i]['colors'] = new_colors
            
            print(f"Cubie {i}: {old_data[idx]['pos']} -> {new_pos}")
            print(f"Colors: {old_data[idx]['colors']} -> {new_colors}")
    
    def rotate_position(self, pos, axis, clockwise):
        x, y, z = pos
        if axis == 'x':
            return [x, -z if clockwise else z, y if clockwise else -y]
        elif axis == 'y':
            return [z if clockwise else -z, y, -x if clockwise else x]
        elif axis == 'z':
            return [-y if clockwise else y, x if clockwise else -x, z]
        return pos
    
    def rotate_colors(self, colors, axis, clockwise):
        new_colors = {}
        
        print(f"  Rotating colors {colors} around {axis}, clockwise={clockwise}")
        
        if axis == 'y':
            if clockwise:
                mapping = {'front': 'right', 'right': 'back', 'back': 'left', 'left': 'front'}
            else:
                mapping = {'front': 'left', 'left': 'back', 'back': 'right', 'right': 'front'}
            for face in ['top', 'bottom']:
                if face in colors:
                    new_colors[face] = colors[face]
                    
        elif axis == 'x':
            if clockwise:
                mapping = {'front': 'top', 'top': 'back', 'back': 'bottom', 'bottom': 'front'}
            else:
                mapping = {'front': 'bottom', 'bottom': 'back', 'back': 'top', 'top': 'front'}
            for face in ['left', 'right']:
                if face in colors:
                    new_colors[face] = colors[face]
                    
        elif axis == 'z':
            if clockwise:
                mapping = {'top': 'left', 'left': 'bottom', 'bottom': 'right', 'right': 'top'}
            else:
                mapping = {'top': 'right', 'right': 'bottom', 'bottom': 'left', 'left': 'top'}
            for face in ['front', 'back']:
                if face in colors:
                    new_colors[face] = colors[face]
        else:
            return colors
        
        for old_face, color in colors.items():
            if old_face in mapping:
                new_face = mapping[old_face]
                new_colors[new_face] = color
            elif old_face not in new_colors:
                new_colors[old_face] = color
        
        print(f"  Result: {new_colors}")
        return new_colors

def draw_sticker(face):
    s = CUBIE_SIZE / 2
    offset = 0.01
    glBegin(GL_QUADS)
    if face == 'front':
        glVertex3f(-s, -s, s + offset)  
        glVertex3f(s, -s, s + offset)   
        glVertex3f(s, s, s + offset)    
        glVertex3f(-s, s, s + offset)   
    elif face == 'back':
        glVertex3f(s, -s, -s - offset)   
        glVertex3f(-s, -s, -s - offset)  
        glVertex3f(-s, s, -s - offset)   
        glVertex3f(s, s, -s - offset)   
    elif face == 'top':
        glVertex3f(-s, s + offset, s)   
        glVertex3f(s, s + offset, s)     
        glVertex3f(s, s + offset, -s)    
        glVertex3f(-s, s + offset, -s)   
    elif face == 'bottom':
        glVertex3f(-s, -s - offset, -s)  
        glVertex3f(s, -s - offset, -s)   
        glVertex3f(s, -s - offset, s)    
        glVertex3f(-s, -s - offset, s)   
    elif face == 'left':
        glVertex3f(-s - offset, -s, s)   
        glVertex3f(-s - offset, s, s)    
        glVertex3f(-s - offset, s, -s)   
        glVertex3f(-s - offset, -s, -s)  
    elif face == 'right':
        glVertex3f(s + offset, -s, -s)   
        glVertex3f(s + offset, s, -s)    
        glVertex3f(s + offset, s, s)    
        glVertex3f(s + offset, -s, s)    
    glEnd()

def draw_cubie(cubie):
    x, y, z = cubie['pos']
    colors = cubie['colors']
    
    if not colors:
        print(f"WARNING: Cubie at {cubie['pos']} has no colors!")
    
    glPushMatrix()
    glTranslatef(x * SPACING, y * SPACING, z * SPACING)
    
    glColor3f(0.05, 0.05, 0.05)
    glutSolidCube(CUBIE_SIZE)
    
    for face, color in colors.items():
        if color in COLORS:
            glColor3fv(COLORS[color])
            draw_sticker(face)
        else:
            print(f"WARNING: Unknown color '{color}' for face '{face}' at {cubie['pos']}")
    
    glPopMatrix()

def draw_cube(cube):
    if cube.is_animating and cube.current_rotation:
        axis = cube.current_rotation['axis']
        angle = cube.current_rotation['angle'] * cube.animation_progress
        animating_indices = cube.current_rotation['indices']
        
        for i, cubie in enumerate(cube.cubies):
            if i not in animating_indices:
                draw_cubie(cubie)
        glPushMatrix()
        if axis == 'x':
            glRotatef(angle, 1, 0, 0)
        elif axis == 'y':
            glRotatef(angle, 0, 1, 0)
        elif axis == 'z':
            glRotatef(angle, 0, 0, 1)
        
        for i in animating_indices:
            draw_cubie(cube.cubies[i])
        
        glPopMatrix()
    else:
        for cubie in cube.cubies:
            draw_cubie(cubie)

def main():
    pygame.init()
    glutInit()
    display = (1000, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Rubik's Cube 3x3 Simulator")

    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glDisable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)

    gluPerspective(45, display[0]/display[1], 0.1, 100.0)
    glTranslatef(0, 0, -10)

    x_rot = y_rot = 0
    dragging = False
    last_mouse = None
    
    cube = SimpleCube()
    
    clock = pygame.time.Clock()
    
    print("=== CONTROLS ===")
    print("Mouse: Drag to rotate view")
    print("U: Up face clockwise")
    print("D: Down face clockwise") 
    print("R: Right face clockwise")
    print("L: Left face clockwise")
    print("F: Front face clockwise")
    print("B: Back face clockwise")
    print("SPACE: Reset")
    print("================")

    while True:
        cube.update_animation()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(x_rot, 1, 0, 0)
        glRotatef(y_rot, 0, 1, 0)
        draw_cube(cube)
        glPopMatrix()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse = pygame.mouse.get_pos()
                    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    
            elif event.type == MOUSEMOTION and dragging:
                x, y = pygame.mouse.get_pos()
                if last_mouse:
                    dx, dy = x - last_mouse[0], y - last_mouse[1]
                    y_rot += dx * 0.2
                    x_rot += dy * 0.2
                last_mouse = (x, y)
                        
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    cube = SimpleCube()
                    print("=== CUBE RESET ===")
                elif event.key == K_u:
                    cube.rotate_layer('y', 1, True)  
                elif event.key == K_d:
                    cube.rotate_layer('y', -1, True)  
                elif event.key == K_r:
                    cube.rotate_layer('x', 1, True)   
                elif event.key == K_l:
                    cube.rotate_layer('x', -1, True)  
                elif event.key == K_f:
                    cube.rotate_layer('z', 1, True)   
                elif event.key == K_b:
                    cube.rotate_layer('z', -1, True)  
                if event.key in [K_u, K_d, K_r, K_l, K_f, K_b]:
                    face_names = {K_u: 'U', K_d: 'D', K_r: 'R', K_l: 'L', K_f: 'F', K_b: 'B'}
                    print(f"=== PRESSED {face_names[event.key]} ===")

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Need: pip install pygame PyOpenGL PyOpenGL_accelerate")
        sys.exit(1)
