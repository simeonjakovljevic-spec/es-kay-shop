"""
Simple 2D Minecraft-like game (mine.py)

Controls:
 - Left / A, Right / D: move
 - Up / W or Space: jump
 - Mouse right click: remove block
 - Mouse left click: place selected block
 - Number keys 1-5: select block type
 - R: reset world
 - Esc or close window: quit

This is a minimal, single-file Python + Pygame example for a block-building sandbox.
"""

import sys
import random
import pygame

# -- Configuration
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

TILE_SIZE = 32
WORLD_WIDTH = 64   # blocks
WORLD_HEIGHT = 32  # blocks

GRAVITY = 0.6
JUMP_SPEED = -12
PLAYER_SPEED = 4

# Colors for block types
BLOCK_TYPES = {
	0: (135, 206, 235),  # sky (empty)
	1: (106, 55, 5),    # dirt
	2: (120, 95, 60),   # stone
	3: (34, 139, 34),   # grass
	4: (194, 178, 128), # sand
	5: (30, 144, 255),  # water (simple)
}

# Starting world function
def generate_world(width, height):
	world = [[0 for _ in range(width)] for _ in range(height)]

	# Base ground level
	ground_level = height // 2 + 3
	for y in range(height):
		for x in range(width):
			if y >= ground_level:
				# deeper = more stone
				depth = y - ground_level
				if depth < 2:
					world[y][x] = 3 if random.random() < 0.4 else 1
				elif depth < 5:
					world[y][x] = 1
				else:
					world[y][x] = 2

	# some random holes and caves
	for _ in range(500):
		x = random.randrange(0, width)
		y = random.randrange(ground_level, height)
		world[y][x] = 0

	# small surface sand near left and right for variety
	for x in range(width // 4, width // 3):
		world[ground_level - 1][x] = 4

	return world


class Camera:
	def __init__(self, w, h):
		self.x = 0
		self.y = 0
		self.width = w
		self.height = h

	def apply(self, rect):
		return rect.move(-self.x, -self.y)

	def center_on(self, px, py):
		halfw = SCREEN_WIDTH // 2
		halfh = SCREEN_HEIGHT // 2
		self.x = max(0, min(px - halfw, self.width - SCREEN_WIDTH))
		self.y = max(0, min(py - halfh, self.height - SCREEN_HEIGHT))


class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.w = TILE_SIZE - 6
		self.h = TILE_SIZE * 1.8
		self.vx = 0
		self.vy = 0
		self.on_ground = False

	def rect(self):
		return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

	def update(self, world):
		# apply gravity
		self.vy += GRAVITY
		self.x += self.vx
		self.collide_axis(world, axis='x')
		self.y += self.vy
		self.on_ground = False
		self.collide_axis(world, axis='y')

	def collide_axis(self, world, axis='x'):
		r = self.rect()
		tiles = get_colliding_tiles(world, r)
		for tx, ty in tiles:
			if world[ty][tx] == 0:
				continue
			block_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
			if r.colliderect(block_rect):
				if axis == 'x':
					if self.vx > 0:
						self.x = block_rect.left - self.w
					elif self.vx < 0:
						self.x = block_rect.right
					self.vx = 0
				else:
					if self.vy > 0:
						self.y = block_rect.top - self.h
						self.vy = 0
						self.on_ground = True
					elif self.vy < 0:
						self.y = block_rect.bottom
						self.vy = 0

	def move_left(self):
		self.vx = -PLAYER_SPEED

	def move_right(self):
		self.vx = PLAYER_SPEED

	def stop(self):
		self.vx = 0

	def jump(self):
		if self.on_ground:
			self.vy = JUMP_SPEED


def get_colliding_tiles(world, rect):
	tiles = []
	left = max(0, rect.left // TILE_SIZE)
	right = min(WORLD_WIDTH - 1, rect.right // TILE_SIZE)
	top = max(0, rect.top // TILE_SIZE)
	bottom = min(WORLD_HEIGHT - 1, rect.bottom // TILE_SIZE)
	for ty in range(top, bottom + 1):
		for tx in range(left, right + 1):
			tiles.append((tx, ty))
	return tiles


def world_to_screen(x, y, cam):
	return x * TILE_SIZE - cam.x, y * TILE_SIZE - cam.y


def main():
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption('MiniCraft - simple 2D block sandbox')
	clock = pygame.time.Clock()

	world = generate_world(WORLD_WIDTH, WORLD_HEIGHT)

	# ensure spawn position is empty
	spawn_x = WORLD_WIDTH // 2
	spawn_y = 0
	for y in range(WORLD_HEIGHT):
		if world[y][spawn_x] != 0:
			spawn_y = y - 3
			break

	player = Player(spawn_x * TILE_SIZE + 6, spawn_y * TILE_SIZE)

	camera = Camera(WORLD_WIDTH * TILE_SIZE, WORLD_HEIGHT * TILE_SIZE)

	selected_block = 1
	show_grid = False
	running = True

	font = pygame.font.SysFont('Arial', 18)

	while running:
		dt = clock.tick(FPS) / 1000.0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_ESCAPE,):
					running = False
				if event.key in (pygame.K_UP, pygame.K_w):
					player.jump()
				if event.key == pygame.K_r:
					world = generate_world(WORLD_WIDTH, WORLD_HEIGHT)
				if event.key == pygame.K_g:
					show_grid = not show_grid
				if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
					selected_block = int(event.unicode)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mx, my = pygame.mouse.get_pos()
				wx = int((mx + camera.x) // TILE_SIZE)
				wy = int((my + camera.y) // TILE_SIZE)
				if 0 <= wx < WORLD_WIDTH and 0 <= wy < WORLD_HEIGHT:
					if event.button == 1:  # left click -> remove block
						if world[wy][wx] != 0:
							world[wy][wx] = 0
					elif event.button == 3:  # right click -> place block
						# place selected block only if empty and not inside player
						if world[wy][wx] == 0:
							# simple check to not place in player rect
							block_rect = pygame.Rect(wx * TILE_SIZE, wy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
							if not player.rect().colliderect(block_rect):
								world[wy][wx] = selected_block

		# continuous key state
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			player.move_left()
		elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			player.move_right()
		else:
			player.stop()

		player.update(world)

		# camera center on player
		player_center_x = player.x + player.w // 2
		player_center_y = player.y + player.h // 2
		camera.center_on(player_center_x, player_center_y)

		# draw background
		screen.fill((100, 149, 237))

		# draw tiles
		# camera.x/y may be floats; convert to int before doing // so we get integer tile ranges
		start_x = max(0, int(camera.x) // TILE_SIZE)
		end_x = min(WORLD_WIDTH, (int(camera.x + SCREEN_WIDTH) // TILE_SIZE) + 2)
		start_y = max(0, int(camera.y) // TILE_SIZE)
		end_y = min(WORLD_HEIGHT, (int(camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 2)

		for y in range(start_y, end_y):
			for x in range(start_x, end_x):
				t = world[y][x]
				if t == 0:
					continue
				color = BLOCK_TYPES.get(t, (255, 255, 255))
				sx, sy = world_to_screen(x, y, camera)
				rect = pygame.Rect(int(sx), int(sy), TILE_SIZE, TILE_SIZE)
				pygame.draw.rect(screen, color, rect)
				# simple shading and border
				pygame.draw.rect(screen, (0, 0, 0), rect, 1)

		# draw player
		pr = player.rect()
		pr_screen = pygame.Rect(int(pr.left - camera.x), int(pr.top - camera.y), pr.width, pr.height)
		pygame.draw.rect(screen, (255, 0, 0), pr_screen)

		# HUD
		hud_y = 6
		text = font.render(f'Block: {selected_block} (1-5)  | Left click remove, Right click place  | R reset', True, (255, 255, 255))
		screen.blit(text, (8, hud_y))

		# show selected block preview at cursor
		mx, my = pygame.mouse.get_pos()
		wx = int((mx + camera.x) // TILE_SIZE)
		wy = int((my + camera.y) // TILE_SIZE)
		if 0 <= wx < WORLD_WIDTH and 0 <= wy < WORLD_HEIGHT:
			px, py = world_to_screen(wx, wy, camera)
			preview_rect = pygame.Rect(int(px), int(py), TILE_SIZE, TILE_SIZE)
			pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2)
			if 0 <= selected_block <= max(BLOCK_TYPES.keys()):
				bcol = BLOCK_TYPES[selected_block]
				preview_inner = preview_rect.inflate(-6, -6)
				pygame.draw.rect(screen, bcol, preview_inner)

		# mini-inventory
		inv_x = SCREEN_WIDTH - 140
		inv_y = 6
		pygame.draw.rect(screen, (0, 0, 0), (inv_x - 6, inv_y - 6, 132, 44))
		for i in range(1, 6):
			bx = inv_x + (i - 1) * 24
			brect = pygame.Rect(bx, inv_y, 22, 22)
			pygame.draw.rect(screen, BLOCK_TYPES.get(i, (200, 200, 200)), brect)
			border = (255, 255, 0) if i == selected_block else (0, 0, 0)
			pygame.draw.rect(screen, border, brect, 2)

		# flip
		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	main()

