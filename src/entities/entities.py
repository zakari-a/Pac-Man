from ..maze.maze_adapter import Tile
from typing import Tuple
import pygame
import random

class Pacman:
    def __init__(self, tilesize, grid):
        self.grid = grid
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.tile_size = tilesize
        self.pac_size = self.tile_size
        self.position = Tuple[int, int]
        self.time = pygame.time.get_ticks()
        self.speed = max(1, tilesize // 12)
        self.counter = 0

    def _find_spawn(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == Tile.SPAWN:
                    self.position = (x * self.tile_size, y * self.tile_size)
                    return
        raise ValueError("No spawn tile found in maze")
    
    def _fast_mouvements(self):
        direction = self.direction
        if self.direction == (0, -1) and self.next_direction == (0, +1):
            return self.next_direction
        elif self.direction == (0, +1) and self.next_direction == (0, -1):
            return self.next_direction
        elif self.direction == (1, 0) and self.next_direction == (-1, 0):
            return self.next_direction
        elif self.direction == (-1, 0) and self.next_direction == (1, 0):
            return self.next_direction
        return direction

    def _get_speed(self):
        x, y = self.position
        t = self.tile_size
        if self.direction == (0, -1) or self.direction == (-1, 0):
            if self.direction == (0, -1):
                distance = y % t
            else:
                distance = x % t
        else:
            if self.direction == (0, 1):
                distance = t - (y % t)
            else:
                distance = t - (x % t)
        if distance == 0:
            distance = t
        if distance >= self.speed:
            return self.speed
        return distance

    def _update_pacposition(self):
        if self.direction == (0, 0) and self.next_direction == (0, 0):
            return
        x, y = self.position
        new_dir = self._fast_mouvements()
        if self.next_direction == new_dir:
            self.direction = new_dir
        else:
            if (x % self.tile_size == 0 and y % self.tile_size == 0):
                nx, ny = self.next_direction
                tx = (x + nx * self.tile_size) // self.tile_size
                ty = (y + ny * self.tile_size) // self.tile_size
                if self.grid[ty][tx] != Tile.WALL:
                    self.direction = self.next_direction
        dx, dy = self.direction
        x, y = self.position
        speed = self._get_speed()
        # print(speed)
        nx = x + (dx * speed)
        ny = y + (dy * speed)
        size = self.pac_size
        corners = [(nx, ny), (nx + size - 1, ny), (nx, ny + size - 1), (nx + size - 1, ny + size - 1)]
        for cx, cy in corners:
            if self.grid[cy // self.tile_size][cx // self.tile_size] == Tile.WALL:
                return
        self.position = (nx, ny)
        
    def _set_pacmouvements(self, key):
        if key == pygame.K_UP:
            self.next_direction = (0, -1)
        elif key == pygame.K_DOWN:
            self.next_direction = (0, +1)
        elif key == pygame.K_LEFT:
            self.next_direction = (-1, 0)
        elif key == pygame.K_RIGHT:
            self.next_direction = (+1, 0)

    def _move_frame(self) -> int:
        c_time = pygame.time.get_ticks()
        if c_time - self.time < 150:
            return 0
        self.time = pygame.time.get_ticks()
        return 1
    
    def eat(self):
        x = self.position[0] + self.pac_size // 2
        y = self.position[1] + self.pac_size // 2
        gx = x // self.tile_size
        gy = y // self.tile_size
        char = self.grid[gy][gx]
        if char in [Tile.PACGUM, Tile.SUPER_PACGUM]:
            self.grid[gy][gx] = Tile.EMPTY

class Ghost:
    def __init__(self, g_type, corner, grid, tilesize):
        self.tile_size = tilesize
        self.grid = grid
        self.time = pygame.time.get_ticks()
        self.type = g_type
        self.position = corner
        self.counter = 0
        self.direction = (0, 0)
        self.speed = max(1, tilesize // 16)

    def _get_speed(self):
            x, y = self.position
            t = self.tile_size
            if self.direction == (0, -1) or self.direction == (-1, 0):
                if self.direction == (0, -1):
                    distance = y % t
                else:
                    distance = x % t
            else:
                if self.direction == (0, 1):
                    distance = t - (y % t)
                else:
                    distance = t - (x % t)
            if distance == 0:
                distance = t
            if distance >= self.speed:
                return self.speed
            return distance

    def _can_move(self, direction):
        if direction == (0, 0):
            return False
        dx, dy = direction
        x, y = self.position
        speed = self._get_speed()
        tx = x + dx * speed
        ty = y + dy * speed
        size = self.tile_size
        corners = [(tx, ty), (tx + size - 1, ty), (tx, ty + size - 1), (tx + size - 1, ty + size - 1)]
        for corner in corners:
            cx, cy = corner
            if self.grid[cy // size][cx // size] == Tile.WALL:
                return False
        return True

    def _move(self):
        if not self._can_move(self.direction):
            return
        dx, dy = self.direction
        x, y = self.position
        speed = self._get_speed()
        nx = x + dx * speed
        ny = y + dy * speed
        self.position = (nx, ny)

    def _valid_directions(self):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valids = []
        for direction in directions:
            if self._can_move(direction):
                valids.append(direction)
        return valids

    def _choose_direction(self):
        valids = self._valid_directions()
        reverse = (-self.direction[0], -self.direction[1])
        normal = [d for d in valids if d != reverse]
        if normal:
            self.direction = random.choice(normal)
        elif valids:
            self.direction = reverse

    def _move_frame(self):
        c_time = pygame.time.get_ticks()
        if c_time - self.time >= 150:
            self.counter += 1
            self.time = pygame.time.get_ticks()

    def _update(self):
        x, y = self.position
        if x % self.tile_size == 0 and y % self.tile_size == 0:
            self._choose_direction()
        self._move()
        self._move_frame()