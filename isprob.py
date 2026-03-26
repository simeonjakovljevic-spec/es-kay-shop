import pygame
import random

# --- CONFIG ---
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), # I
    (0, 0, 255),   # J
    (255, 165, 0), # L
    (255, 255, 0), # O
    (0, 255, 0),   # S
    (128, 0, 128), # T
    (255, 0, 0)    # Z
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],          # I
    [[2, 0, 0],
     [2, 2, 2]],             # J
    [[0, 0, 3],
     [3, 3, 3]],             # L
    [[4, 4],
     [4, 4]],                # O
    [[0, 5, 5],
     [5, 5, 0]],             # S
    [[0, 6, 0],
     [6, 6, 6]],             # T
    [[7, 7, 0],
     [0, 7, 7]]              # Z
]

# --- CLASSES ---
class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.x = COLS // 2 - len(shape[0]) // 2
        self.y = 0
        self.color = COLORS[SHAPES.index(shape)]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    for i, row in enumerate(piece.shape):
        for j, val in enumerate(row):
            if val != 0:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted_pos = [[(x, y) for x in range(COLS) if grid[y][x] == BLACK] for y in range(ROWS)]
    accepted_pos = [x for sub in accepted_pos for x in sub]
    for pos in convert_shape_format(piece):
        if pos not in accepted_pos:
            return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(random.choice(SHAPES))

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, WHITE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except:
                    continue
    if cleared > 0:
        # Move every row above down
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            newKey = (x, y + cleared)
            if y < y:
                locked[newKey] = locked.pop(key)
    return cleared

def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, WHITE)
    surface.blit(label, (10, 10))
    pygame.display.update()

def rotate(piece):
    piece.shape = [list(row) for row in zip(*piece.shape[::-1])]

# --- MAIN GAME ---
def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    rotate(current_piece)
                    if not valid_space(current_piece, grid):
                        # rotate back
                        for _ in range(3):
                            rotate(current_piece)

        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)

        if check_lost(locked_positions):
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()
