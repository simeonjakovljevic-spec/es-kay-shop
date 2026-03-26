"""
iSimple Tetris clone in Python using Pygame

Controls:
 - Left/Right: move piece
 - Down: soft drop
 - Up / X: rotate clockwise
 - Z: rotate counter-clockwise
 - Space: hard drop
 - C: hold piece (toggle)
 - P: pause
 - R: restart after game over

Run:
    pip install -r requirements.txt
    python tetris.py

This is a single-file, self-contained implementation (no external assets required).
"""

import nt
import sys
import random
import math
import time

try:
    import pygame
    from pygame.locals import *
except Exception as e:
    print("This game requires pygame. Run: pip install pygame")
    raise

# Game config
CELL_SIZE = 40
COLUMNS = 10
ROWS = 20
SIDE_PANEL = 200
WIDTH = CELL_SIZE * COLUMNS + SIDE_PANEL
HEIGHT = CELL_SIZE * ROWS
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)

COLORS = [
    (0, 240, 240),  # I - cyan
    (0, 0, 240),    # J - blue
    (240, 160, 0),  # L - orange
    (240, 240, 0),  # O - yellow
    (0, 240, 0),    # S - green
    (160, 0, 240),  # T - purple
    (240, 0, 0),    # Z - red
]

# Tetromino definitions - order follows COLORS
# Each shape is a list of rotations; rotations are lists of rows as strings '.' or 'X'
SHAPES = [
    # I
    [
        ['....', 'XXXX', '....', '....'],
        ['..X.', '..X.', '..X.', '..X.'],
    ],
    # J
    [
        ['X..', 'XXX', '...'],
        ['.XX', '.X.', '.X.'],
        ['...', 'XXX', '..X'],
        ['.X.', '.X.', 'XX.'],
    ],
    # L
    [
        ['..X', 'XXX', '...'],
        ['.X.', '.X.', '.XX'],
        ['...', 'XXX', 'X..'],
        ['XX.', '.X.', '.X.'],
    ],
    # O
    [
        ['.XX', '.XX', '...'],
    ],
    # S
    [
        ['.XX', 'XX.', '...'],
        ['.X.', '.XX', '..X'],
    ],
    # T
    [
        ['.X.', 'XXX', '...'],
        ['.X.', '.XX', '.X.'],
        ['...', 'XXX', '.X.'],
        ['.X.', 'XX.', '.X.'],
    ],
    # Z
    [
        ['XX.', '.XX', '...'],
        ['..X', '.XX', '.X.'],
    ],
]

# Utility: convert shape rotation to list of (x,y) block offsets

def rotation_to_coords(rot):
    h = len(rot)
    w = len(rot[0])
    coords = []
    for y in range(h):
        for x in range(w):
            if rot[y][x] != '.' and rot[y][x] != '\\n':
                coords.append((x, y))
    return coords

SHAPES_COORDS = []
for shape in SHAPES:
    SHAPES_COORDS.append([rotation_to_coords(rot) for rot in shape])

# Pretty benign RNG; use bag system for fair piece distribution
class PieceBag:
    def __init__(self):
        self.bag = []

    def next(self):
        if not self.bag:
            self.bag = list(range(len(SHAPES)))
            random.shuffle(self.bag)
        return self.bag.pop()


class Piece:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.rotation = 0

    def coords(self):
        rots = SHAPES_COORDS[self.kind]
        rot = rots[self.rotation % len(rots)]
        return [(self.x + px, self.y + py) for (px, py) in rot]

    def rotate(self, dir=1):
        self.rotation = (self.rotation + dir) % len(SHAPES_COORDS[self.kind])


class Board:
    def __init__(self, cols=COLUMNS, rows=ROWS):
        self.cols = cols
        self.rows = rows
        # grid stores None or (colorIndex)
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def inside(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows

    def cell(self, x, y):
        if not self.inside(x, y):
            return None
        return self.grid[y][x]

    def can_place(self, piece):
        for (x, y) in piece.coords():
            if not self.inside(x, y) or self.grid[y][x] is not None:
                return False
        return True

    def place(self, piece):
        for (x, y) in piece.coords():
            if 0 <= y < self.rows and 0 <= x < self.cols:
                self.grid[y][x] = piece.kind

    def clear_lines(self):
        new_grid = [row for row in self.grid if not all(cell is not None for cell in row)]
        cleared = self.rows - len(new_grid)
        while len(new_grid) < self.rows:
            new_grid.insert(0, [None] * self.cols)
        self.grid = new_grid
        return cleared


class TetrisGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Tetris (Python)')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.bag = PieceBag()
        self.curr = None
        self.next_piece = None
        self.hold_piece = None
        self.hold_locked = False
        self.spawn_new_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_counter = 0.0
        self.drop_interval = self.get_drop_interval()
        self.game_over = False
        self.paused = False
        self.last_move_time = 0
        self.drop_speed = 1

    def get_drop_interval(self):
        # Seconds per cell fall; increase speed with level
        return max(0.05, 0.8 - (self.level - 1) * 0.07)

    def spawn_new_piece(self):
        if self.next_piece is None:
            k = self.bag.next()
            self.curr = Piece(k, self.board.cols // 2 - 2, -1)
            self.next_piece = Piece(self.bag.next(), self.board.cols + 4, 0)
        else:
            self.curr = Piece(self.next_piece.kind, self.board.cols // 2 - 2, -1)
            self.next_piece = Piece(self.bag.next(), self.board.cols + 4, 0)

        # if cannot place current piece -> game over
        if not self.board.can_place(self.curr):
            self.game_over = True

        self.hold_locked = False

    def hold(self):
        if self.hold_locked:
            return
        if self.hold_piece is None:
            self.hold_piece = Piece(self.curr.kind, 0, 0)
            self.spawn_new_piece()
        else:
            k = self.curr.kind
            self.curr = Piece(self.hold_piece.kind, self.board.cols // 2 - 2, -1)
            self.hold_piece = Piece(k, 0, 0)
            if not self.board.can_place(self.curr):
                self.game_over = True
        self.hold_locked = True

    def hard_drop(self):
        while True:
            p = Piece(self.curr.kind, self.curr.x, self.curr.y + 1)
            p.rotation = self.curr.rotation
            if self.board.can_place(p):
                self.curr.y += 1
            else:
                break
        self.lock_piece()

    def lock_piece(self):
        self.board.place(self.curr)
        cleared = self.board.clear_lines()
        if cleared > 0:
            self.lines += cleared
            # scoring like classic: 1 line 40*(level+1), 2 lines 100, 3 lines 300, 4 lines 1200
            score_map = {1: 40, 2: 100, 3: 300, 4: 1200}
            self.score += score_map.get(cleared, 0) * self.level
            # level up per 10 lines
            self.level = 1 + self.lines // 10
            self.drop_interval = self.get_drop_interval()
        self.spawn_new_piece()

    def rotate_with_wall_kick(self, dir=1):
        old_rot = self.curr.rotation
        self.curr.rotate(dir)
        if self.board.can_place(self.curr):
            return
        # simple wall-kick: try left and right
        for dx in (-1, 1, -2, 2):
            self.curr.x += dx
            if self.board.can_place(self.curr):
                return
            self.curr.x -= dx
        # cannot place -> revert rotation
        self.curr.rotation = old_rot

    def try_move(self, dx, dy):
        p = Piece(self.curr.kind, self.curr.x + dx, self.curr.y + dy)
        p.rotation = self.curr.rotation
        if self.board.can_place(p):
            self.curr.x += dx
            self.curr.y += dy
            return True
        return False

    def soft_drop(self):
        if not self.try_move(0, 1):
            self.lock_piece()

    def update(self, dt):
        if self.paused or self.game_over:
            return
        self.drop_counter += dt
        if self.drop_counter >= self.drop_interval:
            self.drop_counter = 0
            if not self.try_move(0, 1):
                self.lock_piece()

    def draw_grid(self):
        # background
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
                cell = self.board.grid[y][x]
                if cell is not None:
                    color = COLORS[cell]
                    pygame.draw.rect(self.screen, color, rect.inflate(-2, -2))

    def draw_piece(self, piece, at_offset_x=0, at_offset_y=0, ghost=False):
        for (x, y) in piece.coords():
            draw_x = x * CELL_SIZE + at_offset_x
            draw_y = y * CELL_SIZE + at_offset_y
            rect = pygame.Rect(draw_x, draw_y, CELL_SIZE, CELL_SIZE)
            if 0 <= y < self.board.rows:
                base = COLORS[piece.kind]
                if ghost:
                    col = tuple(min(255, int(c * 0.33)) for c in base)
                    pygame.draw.rect(self.screen, col, rect.inflate(-2, -2))
                else:
                    pygame.draw.rect(self.screen, base, rect.inflate(-2, -2))
                    pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_ghost(self):
        ghost = Piece(self.curr.kind, self.curr.x, self.curr.y)
        ghost.rotation = self.curr.rotation
        while True:
            if not self.board.can_place(Piece(ghost.kind, ghost.x, ghost.y + 1)):
                break
            ghost.y += 1
        # draw the ghost piece with a dimmed color
        self.draw_piece(ghost, at_offset_x=0, at_offset_y=0, ghost=True)

    def draw_side_panel(self):
        panel_x = self.board.cols * CELL_SIZE
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(panel_x, 0, SIDE_PANEL, HEIGHT))
        # Next piece
        font = pygame.font.SysFont('Consolas', 20)
        small = pygame.font.SysFont('Consolas', 16)
        title = font.render('NEXT', True, WHITE)
        self.screen.blit(title, (panel_x + 20, 20))
        # draw next box
        box = pygame.Rect(panel_x + 20, 50, CELL_SIZE * 4, CELL_SIZE * 4)
        pygame.draw.rect(self.screen, DARK_GRAY, box)
        next_draw = Piece(self.next_piece.kind, self.board.cols + 1, 1)
        self.draw_piece(next_draw, at_offset_x=panel_x + 20 - self.board.cols * CELL_SIZE, at_offset_y=50)

        # Hold
        title2 = font.render('HOLD', True, WHITE)
        self.screen.blit(title2, (panel_x + 20, 50 + CELL_SIZE * 4 + 20))
        box2 = pygame.Rect(panel_x + 20, 50 + CELL_SIZE * 4 + 50, CELL_SIZE * 4, CELL_SIZE * 4)
        pygame.draw.rect(self.screen, DARK_GRAY, box2)
        if self.hold_piece is not None:
            hold_draw = Piece(self.hold_piece.kind, self.board.cols + 1, 1)
            self.draw_piece(hold_draw, at_offset_x=panel_x + 20 - self.board.cols * CELL_SIZE, at_offset_y=50 + CELL_SIZE * 4 + 50)

        # Score / Lines / Level
        score_t = small.render(f'SCORE: {self.score}', True, WHITE)
        lines_t = small.render(f'LINES: {self.lines}', True, WHITE)
        lvl_t = small.render(f'LEVEL: {self.level}', True, WHITE)
        self.screen.blit(score_t, (panel_x + 20, HEIGHT - 110))
        self.screen.blit(lines_t, (panel_x + 20, HEIGHT - 80))
        self.screen.blit(lvl_t, (panel_x + 20, HEIGHT - 50))

        help_lines = [
            'Controls:',
            '← →  move',
            '↑ / X rotate',
            'Z     rotate ccw',
            'Down  soft drop',
            'Space hard drop',
            'C     hold',
            'P     pause',
        ]
        y = HEIGHT - 300
        for h in help_lines:
            h_s = small.render(h, True, (200, 200, 200))
            self.screen.blit(h_s, (panel_x + 20, y))
            y += 20

    def draw(self):
        self.screen.fill(BLACK)
        # playfield bg
        play_rect = pygame.Rect(0, 0, self.board.cols * CELL_SIZE, self.board.rows * CELL_SIZE)
        pygame.draw.rect(self.screen, GRAY, play_rect)

        # ghost piece
        # draw ghost manually
        ghost = Piece(self.curr.kind, self.curr.x, self.curr.y)
        ghost.rotation = self.curr.rotation
        while True:
            p = Piece(ghost.kind, ghost.x, ghost.y + 1)
            p.rotation = ghost.rotation
            if not self.board.can_place(p):
                break
            ghost.y += 1
        self.draw_piece(ghost, ghost=True)

        # board and blocks
        self.draw_grid()
        # current piece
        self.draw_piece(self.curr)
        # side panel
        self.draw_side_panel()

        if self.paused:
            self.draw_overlay('PAUSED')
        if self.game_over:
            self.draw_overlay('GAME OVER', sub=f'Score: {self.score} - Press R to restart')

        pygame.display.flip()

    def draw_overlay(self, text, sub=None):
        font = pygame.font.SysFont('Consolas', 72)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 190))
        self.screen.blit(s, (0, 0))
        t = font.render(text, True, (255, 240, 240))
        rect = t.get_rect(center=(WIDTH // 2 - SIDE_PANEL // 2, HEIGHT // 2))
        self.screen.blit(t, rect)
        if sub:
            small = pygame.font.SysFont('Consolas', 24)
            st = small.render(sub, True, (255, 255, 255))
            rect2 = st.get_rect(center=(WIDTH // 2 - SIDE_PANEL // 2, HEIGHT // 2 + 60))
            self.screen.blit(st, rect2)

    def restart(self):
        self.board = Board()
        self.bag = PieceBag()
        self.curr = None
        self.next_piece = None
        self.hold_piece = None
        self.hold_locked = False
        self.spawn_new_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_counter = 0
        self.drop_interval = self.get_drop_interval()
        self.game_over = False
        self.paused = False

    def run(self):
        # main game loop
        running = True
        last = time.time()
        key_down_time = 0

        while running:
            now = time.time()
            dt = now - last
            last = now
            # limit dt to avoid big jumps
            dt = min(dt, 0.05)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_p:
                        if not self.game_over: 
                            self.paused = not self.paused
                    if event.key == K_r and self.game_over:
                        self.restart()
                    if event.key == K_SPACE and not self.paused and not self.game_over:
                        self.hard_drop()
                    if event.key == K_c and not self.paused and not self.game_over:
                        self.hold()
                    if event.key == K_UP or event.key == K_x:
                        if not (self.paused or self.game_over):
                            self.rotate_with_wall_kick(1)
                    if event.key == K_z:
                        if not (self.paused or self.game_over):
                            self.rotate_with_wall_kick(-1)
                    if event.key == K_DOWN:
                        if not (self.paused or self.game_over):
                            self.soft_drop()
                    if event.key == K_LEFT:
                        if not (self.paused or self.game_over):
                            self.try_move(-1, 0)
                    if event.key == K_RIGHT:
                        if not (self.paused or self.game_over):
                            self.try_move(1, 0)

            # keyboard polling for smooth movement / soft-repeat
            keys = pygame.key.get_pressed()
            if not (self.paused or self.game_over):
                if keys[K_LEFT]:
                    # small delay between moves for good feel
                    if now - self.last_move_time > 0.1:
                        self.try_move(-1, 0)
                        self.last_move_time = now
                if keys[K_RIGHT]:
                    if now - self.last_move_time > 0.1:
                        self.try_move(1, 0)
                        self.last_move_time = now
                if keys[K_DOWN]:
                    # accelerate falling
                    if now - self.last_move_time > 0.02:
                        if not self.try_move(0, 1):
                            self.lock_piece()
                        self.last_move_time = now

            self.update(dt)
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == '__main__':
    try:
        game = TetrisGame()
        game.run()
    except Exception as e:
        print('An error occurred:', e)
        pygame.quit()
        raise

