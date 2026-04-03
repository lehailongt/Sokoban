# =========================
# SOKOBAN FULL PROJECT (MULTI-FILE STYLE IN ONE SCRIPT FOR COPY)
# =========================
# You should split this into files as described.

import pygame
import os
import sys
from collections import deque

pygame.init()

# =========================
# constants.py
# =========================
WIDTH, HEIGHT = 800, 600
TILE = 48
FPS = 60

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (120,120,120)
GREEN = (0,255,0)
BLUE = (0,0,255)
RED = (255,0,0)

# =========================
# utils.py
# =========================
def load_image(name, color):
    path = os.path.join("images", name)
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path), (TILE, TILE))
    surf = pygame.Surface((TILE, TILE))
    surf.fill(color)
    return surf

# =========================
# LOAD ASSETS
# =========================
wall_img = load_image("wall.png", GRAY)
player_img = load_image("player.png", BLUE)
box_img = load_image("box.png", RED)
target_img = load_image("target.png", GREEN)
floor_img = load_image("floor.png", WHITE)

# =========================
# MAP LOADER
# =========================
def load_map(path):
    with open(path, 'r') as f:
        return [list(line.strip('\n')) for line in f]

# =========================
# GAME CLASS (game.py)
# =========================
class Game:
    def __init__(self, grid):
        self.grid = grid
        self.find_player()

    def find_player(self):
        for y,row in enumerate(self.grid):
            for x,val in enumerate(row):
                if val == 'P':
                    self.px, self.py = x,y

    def move(self, dx, dy):
        nx, ny = self.px + dx, self.py + dy
        nnx, nny = self.px + dx*2, self.py + dy*2

        if self.grid[ny][nx] in [' ', '.']:
            self.grid[self.py][self.px] = ' '
            self.px, self.py = nx, ny
            self.grid[self.py][self.px] = 'P'

        elif self.grid[ny][nx] == 'B':
            if self.grid[nny][nnx] in [' ', '.']:
                self.grid[nny][nnx] = 'B'
                self.grid[ny][nx] = 'P'
                self.grid[self.py][self.px] = ' '
                self.px, self.py = nx, ny

    def draw(self, screen):
        for y,row in enumerate(self.grid):
            for x,val in enumerate(row):
                screen.blit(floor_img, (x*TILE, y*TILE))
                if val == '#':
                    screen.blit(wall_img, (x*TILE, y*TILE))
                elif val == 'B':
                    screen.blit(box_img, (x*TILE, y*TILE))
                elif val == '.':
                    screen.blit(target_img, (x*TILE, y*TILE))
                elif val == 'P':
                    screen.blit(player_img, (x*TILE, y*TILE))

# =========================
# SIMPLE IDA* (solver/ida_star.py)
# =========================
def heuristic(state, targets):
    # Manhattan distance sum
    total = 0
    for box in state['boxes']:
        total += min(abs(box[0]-t[0]) + abs(box[1]-t[1]) for t in targets)
    return total


def ida_star(start_state, targets):
    bound = heuristic(start_state, targets)

    def search(state, g, bound):
        f = g + heuristic(state, targets)
        if f > bound:
            return f
        if set(state['boxes']) == set(targets):
            return "FOUND"

        min_bound = float('inf')

        for dx, dy, move in [(0,-1,'U'),(0,1,'D'),(-1,0,'L'),(1,0,'R')]:
            new_state = try_move(state, dx, dy)
            if not new_state: continue

            t = search(new_state, g+1, bound)
            if t == "FOUND":
                state['path'] += move
                return "FOUND"
            if t < min_bound:
                min_bound = t

        return min_bound

    while True:
        t = search(start_state, 0, bound)
        if t == "FOUND":
            return start_state['path']
        if t == float('inf'):
            return None
        bound = t


def try_move(state, dx, dy):
    px, py = state['player']
    nx, ny = px+dx, py+dy

    if (nx,ny) in state['walls']:
        return None

    new_boxes = set(state['boxes'])

    if (nx,ny) in new_boxes:
        nnx, nny = nx+dx, ny+dy
        if (nnx,nny) in state['walls'] or (nnx,nny) in new_boxes:
            return None
        new_boxes.remove((nx,ny))
        new_boxes.add((nnx,nny))

    return {
        'player': (nx,ny),
        'boxes': new_boxes,
        'walls': state['walls'],
        'path': state['path']
    }

# =========================
# MENU (menu.py)
# =========================
def menu(screen):
    font = pygame.font.SysFont(None, 50)
    while True:
        screen.fill(BLACK)
        text = font.render("Press 1: Play | 2: Editor", True, WHITE)
        screen.blit(text, (100, 250))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                if event.key == pygame.K_2:
                    return "editor"

        pygame.display.flip()

# =========================
# EDITOR (editor.py)
# =========================
def editor(screen):
    grid = [[' ' for _ in range(10)] for _ in range(10)]
    current = '#'

    while True:
        screen.fill(BLACK)

        for y in range(10):
            for x in range(10):
                rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                pygame.draw.rect(screen, WHITE, rect, 1)

                if grid[y][x] == '#': screen.blit(wall_img, rect)
                elif grid[y][x] == 'B': screen.blit(box_img, rect)
                elif grid[y][x] == 'P': screen.blit(player_img, rect)
                elif grid[y][x] == '.': screen.blit(target_img, rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: current = '#'
                if event.key == pygame.K_2: current = 'B'
                if event.key == pygame.K_3: current = 'P'
                if event.key == pygame.K_4: current = '.'
                if event.key == pygame.K_s:
                    with open("maps/custom.txt","w") as f:
                        for row in grid:
                            f.write(''.join(row)+"\n")

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                x//=TILE; y//=TILE
                grid[y][x] = current

        pygame.display.flip()

# =========================
# MAIN (main.py)
# =========================
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    while True:
        choice = menu(screen)

        if choice == "editor":
            editor(screen)

        if choice == "play":
            if not os.path.exists("maps/level1.txt"):
                print("Missing maps/level1.txt")
                return

            grid = load_map("maps/level1.txt")
            game = Game(grid)

            running = True
            while running:
                screen.fill(BLACK)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP: game.move(0,-1)
                        if event.key == pygame.K_DOWN: game.move(0,1)
                        if event.key == pygame.K_LEFT: game.move(-1,0)
                        if event.key == pygame.K_RIGHT: game.move(1,0)

                game.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)

if __name__ == "__main__":
    main()