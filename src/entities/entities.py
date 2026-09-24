from __future__ import annotations

from src.maze.maze_adapter import Tile
from src.assets_manager.assetmanager import GhostType, AssetManager
from collections import deque
from typing import Any
from enum import Enum
import pygame


class PacState(Enum):
    """It represents the pacman state."""
    DYING = 0
    ALIVE = 1


class Mouvements:
    """It represents basic mouvement logic that should be inherited by the
    pacman and the ghosts."""
    @staticmethod
    def _get_speed(tile_size: int, position: tuple,
                   direction: tuple, speed: float) -> int | Any:
        """It calculates the suitable speed for the entities.
Args:
    tile_size(int): the size of a tile.
    position(tuple): the entetie's position.
    direction(tuple): the entetie's direction.
    speed(int): the default speed.
Returns:
    int: The computed speed.
"""
        x, y = position
        t = tile_size
        if direction == (0, -1) or direction == (-1, 0):
            if direction == (0, -1):
                distance = y % t
            else:
                distance = x % t
        else:
            if direction == (0, 1):
                distance = t - (y % t)
            else:
                distance = t - (x % t)
        if distance == 0:
            distance = t
        if distance >= speed:
            return speed
        return distance

    @staticmethod
    def _can_move(direction: tuple, position: tuple, o_speed: float,
                  tile_size: int, grid: list[list[Tile]]) -> bool | tuple:
        """It checks if the entity can move in the given direction.
Args:
    direction(tuple): the entetie's direction.
    position(tuple): the entetie's position.
    o_speed(int): the entity's original speed.
    tile_size(int): the size of a tile.
    grid(list[list[Tile]]): the maze grid.
Returns:
    bool | tuple: True if the entity can move,
    False otherwise. If True, returns the new position.
"""
        if direction == (0, 0):
            return False
        dx, dy = direction
        x, y = position
        speed = Mouvements._get_speed(tile_size, position,
                                      direction, o_speed)
        tx = x + dx * speed
        ty = y + dy * speed
        size = tile_size
        corners = [(tx, ty), (tx + size - 1, ty),
                   (tx, ty + size - 1), (tx + size - 1, ty + size - 1)]
        for cx, cy in corners:
            px = cx // tile_size
            py = cy // tile_size
            if grid[py][px] == Tile.WALL:
                return False
        return (tx, ty)


class Pacman(Mouvements):
    """It represents the pacman entity."""
    def __init__(self, tilesize: int,
                 grid: list[list[Tile]], assets: AssetManager):
        """Initializes the pacman entity.
    Args:
        tilesize(int): the size of a tile.
        grid(list[list[Tile]]): the maze grid.
        assets(AssetManager): the asset manager.
    Returns:
        None
    """
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
        self.speed = max(1, round(tilesize / 12))
        self.counter = 0
        self.death_start = 0
        self.super = 0
        self.super_time = 0
        self.mode = PacState.ALIVE

    def _reset(self) -> None:
        """Resets the pacman entity to its initial state.
        Args:
            None
        Returns:
            None
        """
        self.counter = 0
        self.death_start = 0
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.state = self.assets.pacman
        self.position = self.spawn

    def _find_spawn(self) -> None:
        """Finds the spawn position of the pacman in the maze grid.
        Args:
            None
        Returns:
            None
        """
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == Tile.SPAWN:
                    self.position = (x * self.tile_size, y * self.tile_size)
                    self.spawn = (x * self.tile_size, y * self.tile_size)
                    return
        raise ValueError("No spawn tile found in maze")

    def _fast_mouvements(self) -> tuple:
        """It checks if the pacman can move in
        the opposite direction of its current direction.
        Args:
            None
        Returns:
            tuple: The direction the pacman can move.
        """
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

    def _update_pacposition(self) -> None:
        """Updates the pacman's position based
        on its current direction and speed.
        Args:
            None
        Returns:
            None
        """
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
        result = self._can_move(self.direction, self.position,
                                self.speed, self.tile_size, self.grid)
        if isinstance(result, tuple):
            self.position = (result[0], result[1])

    def _set_pacmouvements(self, key: Any) -> None:
        """Sets the next direction of the pacman based on the key pressed.
        Args:
            key(Any): The key pressed.
        Returns:
            None
        """
        if key == pygame.K_UP:
            self.next_direction = (0, -1)
        elif key == pygame.K_DOWN:
            self.next_direction = (0, +1)
        elif key == pygame.K_LEFT:
            self.next_direction = (-1, 0)
        elif key == pygame.K_RIGHT:
            self.next_direction = (+1, 0)

    def _move_frame(self) -> int:
        """Moves the pacman by one frame.
        Args:
            None
        Returns:
            int: 1 if the pacman moved, 0 otherwise.
        """
        c_time = pygame.time.get_ticks()
        if c_time - self.time < 150:
            return 0
        self.time = pygame.time.get_ticks()
        return 1

    def eat(self, ghosts: list[Ghost],
            pacgum_points: int, supergum_points: int) -> int:
        """Checks if the pacman is on a pacgum or
        super pacgum tile and eats it.
        Args:
            ghosts(list[Ghost]): The list of ghosts in the game.
            pacgum_points(int): The points awarded for eating a pacgum.
            supergum_points(int): The points awarded
                                for eating a super pacgum.
        Returns:
            int: The points awarded for eating the tile.
        """
        score = 0
        x = self.position[0] + self.pac_size // 2
        y = self.position[1] + self.pac_size // 2
        gx = x // self.tile_size
        gy = y // self.tile_size
        char = self.grid[gy][gx]
        if char in [Tile.PACGUM, Tile.SUPER_PACGUM]:
            if char == Tile.SUPER_PACGUM:
                self.super = 1
                self.super_time = pygame.time.get_ticks()
                score += supergum_points
                for ghost in ghosts:
                    ghost.was_dead = 0
            elif char == Tile.PACGUM:
                score += pacgum_points
            self.grid[gy][gx] = Tile.EMPTY
        return score

    def _go_normal(self) -> None:
        """Sets the pacman to normal state after super state ends.
        Args:
            None
        Returns:
            None
        """
        c_time = pygame.time.get_ticks()
        if c_time - self.super_time >= 50000:
            self.super = 0

    def check_collision(self, ghosts: list[Ghost], invincible: bool) -> tuple:
        """Checks if the pacman collides with any ghost.
        Args:
            ghosts(list[Ghost]): The list of ghosts in the game.
            invincible(bool): Whether the pacman is invincible.
        Returns:
            tuple: A tuple containing the collision
            result and the ghost's position.
        """
        margin = int(self.tile_size * 0.2)
        px = self.position[0] + margin
        py = self.position[1] + margin
        p_size = self.pac_size - margin * 2
        for ghost in ghosts:
            if not ghost.alive:
                continue
            pos = ghost.position
            g_size = ghost.tile_size - margin * 2
            gx = pos[0] + margin
            gy = pos[1] + margin
            overlapping = (px < gx + g_size and px + p_size > gx
                           and py < gy + g_size and py + p_size > gy)
            if overlapping:
                if self.super and ghost.was_dead == 0:
                    return (2, pos)
                if invincible:
                    return (0, (-1, -1))
                self.state = self.assets.pacman_death
                return (1, pos)
        return (0, (-1, -1))


class Ghost(Mouvements):
    """It represents the ghost entity."""
    def __init__(self, g_type: GhostType, corner: tuple,
                 grid: list[list[Tile]], assets: AssetManager,
                 ghost_eyes: pygame.Surface):
        """Initializes the ghost entity.
        Args:
            g_type(GhostType): The type of the ghost.
            corner(tuple): The starting corner of the ghost.
            grid(list[list[Tile]]): The game grid.
            assets(AssetManager): The asset manager.
        Returns:
            None
        """
        self.tile_size = assets.tile_size
        self.grid = grid
        self.base_corner = corner
        self.time = pygame.time.get_ticks()
        self.type = g_type
        self.position = corner
        self.counter = 0
        self.direction = (0, 0)
        self.speed = max(0.6, round(self.tile_size / 20))
        self.alive = True
        self.death_start = 0
        self.was_dead = 0
        self.one_turn = False
        self.arrived = 0
        self.distancetop = float('inf')
        self.eyes: pygame.Surface = ghost_eyes

    def _reset(self) -> None:
        """Resets the ghost entity to its initial state.
        Args:
            None
        Returns:
            None
        """
        self.counter = 0
        self.death_start = 0
        self.direction = (0, 0)
        self.position = self.base_corner
        self.alive = True

    def _move(self) -> None:
        """Moves the ghost entity based on its current direction and speed.
        Args:
            None
        Returns:
            None
        """
        move = self._can_move(self.direction, self.position, self.speed,
                              self.tile_size, self.grid)
        if isinstance(move, bool):
            return
        self.position = (move[0], move[1])

    # def _valid_directions(self) -> list[tuple]:
    #     directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    #     valids = []
    #     for direction in directions:
    #         if self._can_move(direction):
    #             valids.append(direction)
    #     return valids

    def _death_time(self) -> None:
        """Manages the ghost's death time.
        Args:
            None
        Returns:
            None
        """
        if not self.alive:
            c_time = pygame.time.get_ticks()
            if c_time - self.death_start >= 6000:
                self.alive = True

    def _choose_cheapest(self,
                         dist_map: dict[tuple, int],
                         turn: bool, frightened: bool) -> list:
        """Chooses the cheapest direction for the ghost
        to move based on the distance map.
        Args:
            dist_map (dict[tuple, int]): The distance map.
            turn (bool): Whether the ghost is turning.
            frightened (bool): Whether the ghost is frightened.
        Returns:
            list: The list of chosen directions.
        """
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        x, y = self.position
        if not turn or self.arrived == 0:
            reverse = (-self.direction[0], -self.direction[1])
            normal = [d for d in directions if d != reverse]
            directions = normal if normal else directions
            # self.one_turn = 0
        # elif frightened and self.one_turn == 1
        b_direction = directions[0]
        b_distance = float('-inf') if frightened else float('inf')
        for direction in directions:
            if isinstance(self._can_move(direction, self.position, self.speed,
                                         self.tile_size, self.grid), bool):
                continue
            dx, dy = direction
            nx = (x + dx * self.tile_size) // self.tile_size
            ny = (y + dy * self.tile_size) // self.tile_size
            if frightened:
                distance = dist_map.get((nx, ny), float('-inf'))
            else:
                distance = dist_map.get((nx, ny), float('inf'))
            if ((not frightened and distance < b_distance)
                    or (frightened and distance > b_distance)):
                b_distance = distance
                b_direction = direction
            # elif frightened and distance > b_distance:
            #     b_distance = distance
            #     b_direction = direction
        if frightened:
            self.distancetop = b_distance
        if frightened and b_distance <= 1:
            self.arrived = 1
        else:
            self.arrived = 0
        return [b_direction] if b_direction else []

    def _choose_direction(self, dist_map: dict[tuple, int],
                          turn: bool, frightened: Any) -> None:
        """Chooses the direction for the ghost
        to move based on the distance map.
        Args:
            dist_map (dict[tuple, int]): The distance map.
            turn (bool): Whether the ghost is turning.
            frightened (bool): Whether the ghost is frightened.
        Returns:
            None
        """
        # valids = self._valid_directions()
        # if len(valids) > 1:
        valids = self._choose_cheapest(dist_map, turn, frightened)
        if valids:
            self.direction = valids[0]

    def _move_frame(self) -> None:
        """Moves the ghost by one frame.
        Args:
            None
        Returns:
            None
        """
        c_time = pygame.time.get_ticks()
        if c_time - self.time >= 150:
            self.counter += 1
            self.time = pygame.time.get_ticks()

    def _update(self, pacman: Pacman, red_pos: tuple[int, int]) -> None:
        """Updates the ghost's state and position based
        on the pacman's position and the distance map.
        Args:
            pacman (Pacman): The pacman entity.
            red_pos (tuple[int, int]): The position of the red ghost.
        Returns:
            None
        """
        x, y = self.position
        frightened = pacman.super and (self.was_dead == 0)
        if x % self.tile_size == 0 and y % self.tile_size == 0:
            dist_map = self.pathfinder(pacman, red_pos)
            if not frightened:
                turn = False
            else:
                turn = True if self.distancetop <= 7 else False
                # if self.distancetop <= 4:
                #     turn = True
                # else:
                #     turn = False
            self._choose_direction(dist_map, turn, frightened)
        # self._move()
        self._move_frame()

    def _chase_type(self, pacman: Pacman,
                    red_pos: tuple[int, int]) -> tuple[int, int]:
        """Determines the target position for
        the ghost based on its type and the pacman's state.
        Args:
            pacman (Pacman): The pacman entity.
            red_pos (tuple[int, int]): The position of the red ghost.
        Returns:
            tuple[int, int]: The target position for the ghost.
        """
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
                    return (self.base_corner[0] // self.tile_size,
                            self.base_corner[1] // self.tile_size)
            elif self.type == GhostType.BLUE:
                rx = red_pos[0] // self.tile_size
                ry = red_pos[1] // self.tile_size
                ref_px = px + pdx * 2
                ref_py = py + pdy * 2
                target_x = rx + 2 * (ref_px - rx)
                target_y = ry + 2 * (ref_py - ry)
                return (target_x, target_y)
        else:
            # return (self.base_corner[0] // self.tile_size,
            #         self.base_corner[1] // self.tile_size)
            return (px, py)

    def _get_neighbours(self, position: tuple) -> list:
        """Returns the valid neighbouring positions
        for the ghost based on its current position.
        Args:
            position (tuple[int, int]): The current position of the ghost.
        Returns:
            list: The list of valid neighbouring positions.
        """
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

    def pathfinder(self, pacman: Pacman,
                   red_pos: tuple[int, int]) -> dict[tuple, int]:
        """Generates a distance map for the ghost to chase
        the pacman based on its type and the maze grid.
        Args:
            pacman (Pacman): The pacman entity.
            red_pos (tuple[int, int]): The position of the red ghost.
        Returns:
            dict[tuple, int]: The distance map.
        """
        start_point = self._chase_type(pacman, red_pos)
        grid = self.grid
        h = len(grid)
        w = len(grid[0])
        x, y = start_point
        if (x < 0 or x >= w) or (y < 0 or y >= h) or grid[y][x] == Tile.WALL:
            start_point = (pacman.position[0] // self.tile_size,
                           pacman.position[1] // self.tile_size)
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

    def _update_state(self, pacman: Pacman) -> None:
        """Updates the ghost's state based on the pacman's state.
        Args:
            pacman (Pacman): The pacman entity.
        Returns:
            None
        """
        self._death_time()
        if not pacman.super:
            self.was_dead = 0
