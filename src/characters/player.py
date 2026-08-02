import pygame
from enum import Enum
from ..maze.maze_adapter import Tile



class Direction(Enum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3


class PacMan():
    def __init__(self, x, y) -> None:
        self.nb_frames = 3
        self.frame = 0
        self.anim_frame = 0.0
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.speed = 0.08
        self.x = float(x)
        self.y = float(y)

    def _set_pacmouvements(self, key):
        if key == pygame.K_UP:
            self.next_direction = Direction.UP
        elif key == pygame.K_DOWN:
            self.next_direction = Direction.DOWN
        elif key == pygame.K_LEFT:
            self.next_direction = Direction.LEFT
        elif key == pygame.K_RIGHT:
            self.next_direction = Direction.RIGHT

    def _get_next_pos(self, direc, grid_width, grid_height,
                      cx, cy):
        cx %= grid_width
        cy %= grid_height
        if direc == Direction.UP:
            cy -= 1
        elif direc == Direction.DOWN:
            cy += 1
        elif direc == Direction.LEFT:
            cx -= 1
        elif direc == Direction.RIGHT:
            cx += 1
        return cx % grid_width, cy % grid_height
    
    def _update_position(self, width, height) -> tuple[float]:
        next_x, next_y = self.x, self.y
        if self.direction == Direction.UP:
            next_y -= self.speed
        elif self.direction == Direction.DOWN:
            next_y += self.speed
        elif self.direction == Direction.LEFT:
            next_x -= self.speed
        elif self.direction == Direction.RIGHT:
            next_x += self.speed

        next_x %= width
        next_y %= height
        return (next_x, next_y)
    
    def _get_rotation(self):
        if self.direction == Direction.RIGHT:   # limen
            return 0
        elif self.direction == Direction.UP:  # lfo9
            return 90
        elif self.direction == Direction.LEFT:  # lisser
            return 180
        elif self.direction == Direction.DOWN:   # lte7t
            return 270
        return 0

    def move(self, grid) -> None:
        h, w = len(grid), len(grid[0])

        cx, cy = round(self.x), round(self.y)
        is_centered_x = abs(self.x - cx) <= self.speed * 0.50
        is_centered_y = abs(self.y - cy) <= self.speed * 0.50

        if self.next_direction != self.direction:
            if is_centered_x and is_centered_y:
                nx, ny = self._get_next_pos(self.next_direction, w, h, cx, cy)
                if grid[ny][nx] != Tile.WALL:
                    self.x, self.y = float(cx), float(cy)
                    self.direction = self.next_direction

        next_x, next_y = self._update_position(w, h)
        ahead_x, ahead_y = self._get_next_pos(self.direction, w, h, cx, cy)
        if grid[ahead_y][ahead_x] == Tile.WALL:
            if self.direction == Direction.RIGHT and next_x > cx:
                next_x = float(cx)
            elif self.direction == Direction.LEFT and next_x < cx:
                next_x = float(cx)
            elif self.direction == Direction.DOWN and next_y > cy:
                next_y = float(cy)
            elif self.direction == Direction.UP and next_y < cy:
                next_y = float(cy)

        self.x, self.y = next_x, next_y

    
    def get_frame(self, frames):
        img = frames[self.frame]
        angle = self._get_rotation()
        img = pygame.transform.rotate(img, angle)
        return img

    def update(self) -> None:
        self.anim_frame += 0.1
        self.frame = int(self.anim_frame) % self.nb_frames
