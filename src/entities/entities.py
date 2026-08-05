from ..maze.maze_adapter import Tile
from ..assets.assetmanager import GhostType
from typing import Tuple
from collections import deque
import pygame
import random

class Pacman:
    def __init__(self, tilesize, grid, assets):
        self.grid = grid
        self.assets = assets
        self.state = assets.pacman
        self.spawn = (0, 0)
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.tile_size = tilesize
        self.pac_size = self.tile_size
        self.position = self.spawn
        self.time = pygame.time.get_ticks()
        self.speed = max(1, tilesize // 9)
        self.counter = 0
        self.death_start = 0
        self.super = 0
        self.super_time = 0

    def _reset(self):
        self.counter = 0
        self.death_start = 0
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.state = self.assets.pacman
        self.position = self.spawn

    def _find_spawn(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == Tile.SPAWN:
                    self.position = (x * self.tile_size, y * self.tile_size)
                    self.spawn = (x * self.tile_size, y * self.tile_size)
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
    
    def eat(self, ghosts):
        x = self.position[0] + self.pac_size // 2
        y = self.position[1] + self.pac_size // 2
        gx = x // self.tile_size
        gy = y // self.tile_size
        char = self.grid[gy][gx]
        if char in [Tile.PACGUM, Tile.SUPER_PACGUM]:
            if char == Tile.SUPER_PACGUM:
                self.super = 1
                self.super_time = pygame.time.get_ticks()
                for ghost in ghosts:
                    ghost.was_dead = 0
            self.grid[gy][gx] = Tile.EMPTY
    
    def _go_normal(self):
        c_time = pygame.time.get_ticks()
        if c_time - self.super_time >= 20000:
            self.super = 0
            
    def check_collision(self, ghosts):
        x = (self.position[0] + self.pac_size // 2)// self.tile_size
        y = (self.position[1] + self.pac_size // 2) // self.tile_size
        for ghost in ghosts:
            pos = ghost.position
            gx = (pos[0] + self.pac_size // 2) // self.tile_size
            gy = (pos[1] + self.pac_size // 2) // self.tile_size
            if gx == x and y == gy and not self.super:
                self.state = self.assets.pacman_death
                return (1, pos)
            elif gx == x and y == gy and self.super and ghost.was_dead == 1:
                self.state = self.assets.pacman_death
                return (1, pos)
            elif gx == x and y == gy and self.super and ghost.alive:
                return (2, pos)
        return (0, (-1, -1))

class Ghost:
    def __init__(self, g_type, corner, grid, assets):
        self.tile_size = assets.tile_size
        self.grid = grid
        self.base_corner = corner
        self.time = pygame.time.get_ticks()
        self.type = g_type
        self.position = corner
        self.counter = 0
        self.direction = (0, 0)
        self.speed = max(1, self.tile_size // 14)
        self.alive = True
        self.death_start = 0
        self.was_dead = 0

    def _reset(self):
        self.counter = 0
        self.death_start = 0
        self.direction = (0, 0)
        self.position = self.base_corner

    def _get_position(self):
        return self.position

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

    # def _get_distance(self, x, y, tx, ty):
    #     return ((tx - x) ** 2 + (ty - y) ** 2)

    # def _choose_closest(self, target):
    #     directions = self._valid_directions()
    #     reverse = (-self.direction[0], -self.direction[1])
    #     normal = [d for d in directions if d != reverse]
    #     final = normal if normal else directions
    #     tx = target[0] // self.tile_size
    #     ty = target[1] // self.tile_size
    #     gx = self.position[0] // self.tile_size
    #     gy = self.position[1] // self.tile_size
    #     b_direction = None
    #     b_distance = None
    #     for direction in final:
    #         x, y = direction
    #         nx = gx + x
    #         ny = gy + y
    #         distance = self._get_distance(nx, ny, tx, ty)
    #         if b_distance is None or distance < b_distance:
    #             b_distance = distance
    #             b_direction = direction
    #     self.direction = b_direction

    def _death_time(self):
        if not self.alive:
            c_time = pygame.time.get_ticks()
            if c_time - self.death_start >= 10000:
                self.alive = True

    def _choose_cheapest(self, directions, dist_map):
        x, y = self.position
        reverse = (-self.direction[0], -self.direction[1])
        normal = [d for d in directions if d != reverse]
        final = normal if normal else directions
        b_direction = final[0]
        b_distance = float('inf')
        for direction in final:
            dx, dy = direction
            nx = (x + dx * self.tile_size) // self.tile_size
            ny = (y + dy * self.tile_size) // self.tile_size
            distance = dist_map.get((nx, ny), float('inf'))
            if distance < b_distance:
                b_distance = distance
                b_direction = direction 
        return [b_direction] if b_direction else []

    def _choose_direction(self, dist_map):
        valids = self._valid_directions()
        if len(valids) > 1:
            valids = self._choose_cheapest(valids, dist_map)
        if valids:
            self.direction = valids[0]

    def _move_frame(self):
        c_time = pygame.time.get_ticks()
        if c_time - self.time >= 150:
            self.counter += 1
            self.time = pygame.time.get_ticks()

    def _update(self, pacman, red_pos):
        x, y = self.position
        if x % self.tile_size == 0 and y % self.tile_size == 0:
            dist_map = self.pathfinder(pacman, red_pos)
            self._choose_direction(dist_map)
        self._move()
        self._move_frame()
    
    def _chase_type(self, pacman, red_pos):
        px = pacman.position[0] // self.tile_size
        py = pacman.position[1] // self.tile_size
        pdx = pacman.direction[0]
        pdy = pacman.direction[1]
        if not pacman.super or self.was_dead:
            if self.type == GhostType.RED:
                return (px, py)
            elif self.type == GhostType.PINK:
                return (px + pdx * 4, py + pdy * 4)
            elif self.type == GhostType.ORANGE:
                x = self.position[0] // self.tile_size
                y = self.position[1] // self.tile_size
                distance = (x - px) ** 2 + (y - py) ** 2
                if distance > 64:
                    return (px, py)
                else:
                    return (self.base_corner[0] // self.tile_size, self.base_corner[1] // self.tile_size)
            elif self.type == GhostType.BLUE:
                rx = red_pos[0] // self.tile_size
                ry = red_pos[1] // self.tile_size
                ref_px = px + pdx * 2
                ref_py = py + pdy * 2
                target_x = rx + 2 * (ref_px - rx)
                target_y = ry + 2 * (ref_py - ry)
                return (target_x, target_y)
        else:
            return (self.base_corner[0] // self.tile_size, self.base_corner[1] // self.tile_size)
        return (px, py)

    def _get_neighbours(self, position):
        valids = []
        grid = self.grid
        width = len(grid[0])
        height = len(grid)
        x, y = position
        if y - 1 >= 0 and grid[y - 1][x] != Tile.WALL:
            valids.append((x, y - 1))
        if y + 1 < height and grid[y + 1][x] != Tile.WALL:
            valids.append((x, y + 1))
        if x - 1 >= 0 and grid[y][x - 1] != Tile.WALL:
            valids.append((x - 1, y))
        if x + 1 < width and grid[y][x + 1] != Tile.WALL:
            valids.append((x + 1, y))
        return valids

    def pathfinder(self, pacman, red_pos):
        start_point = self._chase_type(pacman, red_pos)
        grid = self.grid
        h = len(grid)
        w = len(grid[0])
        x, y = start_point
        if (x < 0 or x >= w) or (y < 0 or y >= h) or grid[y][x] == Tile.WALL:
            start_point = (pacman.position[0] // self.tile_size, pacman.position[1] // self.tile_size)
        visited = {start_point}
        queue = deque([start_point])
        result = {start_point: 0}
        while len(queue) > 0:
            chosen = queue.popleft()
            distance = result[chosen]
            neighbours = self._get_neighbours(chosen)
            for neighbour in neighbours:
                if neighbour not in visited:
                    queue.append(neighbour)
                    visited.add(neighbour)
                    result[(neighbour)] = distance + 1
        return result