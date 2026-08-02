from ..maze.maze_adapter import Tile
from ..assets.assetmanager import GhostType
from .player import Direction
from collections import deque



class Ghost:
    def __init__(self, x, y, ghost_type,
                 corner, grid) -> None:
        self.type = ghost_type
        self.corner = corner
        self.x = float(x)
        self.y = float(y)
        self.direction = Direction.LEFT
        self.speed = 0.04
        self.frame = 0
        self.anim_frame = 0.0
        self.nb_frames = 3

    def _get_next_pos(self, direction, grid_width, grid_height,
                       cx, cy) -> tuple[int, int]:
        cx %= grid_width
        cy %= grid_height
        if direction == Direction.UP:
            cy -= 1
        elif direction == Direction.DOWN:
            cy += 1
        elif direction == Direction.LEFT:
            cx -= 1
        elif direction == Direction.RIGHT:
            cx += 1
        return cx % grid_width, cy % grid_height

    def _get_neighbors(self, x, y, grid) -> list[tuple[int, int]]:
        neighbors: list[tuple[int, int]] = []
        h, w = len(grid), len(grid[0])
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = (x + dx) % w, (y + dy) % h
            if grid[ny][nx] != Tile.WALL:
                neighbors.append((nx, ny))
        return neighbors

    def find_path(self, start, target, grid) -> list[tuple[int, int]]:
        queue: deque[tuple[int, int]] = deque([start])
        visited: set[tuple[int, int]] = set()
        parent: dict[tuple[int, int], tuple[int, int]] = {}
        parent[start] = None
        visited.add(start)

        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                cur = current
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                return path[::-1]
            for neighbor in self._get_neighbors(current[0], current[1], grid):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return []
    
    def _set_direction(self, next_pos, cx,
                       cy) -> None:
        dx = next_pos[0] - cx
        dy = next_pos[1] - cy
        if dx > 1:
            self.direction = Direction.LEFT
        elif dx < -1:
            self.direction = Direction.RIGHT
        elif dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP

    def _update_position(self, width, height) -> tuple[float, float]:
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

    def _ghost_chase(self, grid, pacpos, pacdirection) -> tuple[int, int]:
        width = len(grid[0])
        height = len(grid)
        x, y = round(pacpos[0]), round(pacpos[1])
        if self.type == GhostType.ORANGE:
            if pacdirection == Direction.UP:
                y -= 4
            elif pacdirection == Direction.DOWN:
                y += 4
            elif pacdirection == Direction.LEFT:
                x -= 4
            elif pacdirection == Direction.RIGHT:
                x += 4
        
        if self.type == GhostType.PINK:
            if pacdirection == Direction.UP:
                y += 4
            elif pacdirection == Direction.DOWN:
                y -= 4
            elif pacdirection == Direction.LEFT:
                x += 4
            elif pacdirection == Direction.RIGHT:
                x -= 4
        
        if self.type == GhostType.RED:
            if (self.x - x) ** 2 + (self.y - y) ** 2 < 64:
                x, y = 1, height - 2
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        return (x, y)            

    def move(self, grid,  pacpos, pacdirection):
        cx, cy = round(self.x), round(self.y)
        w = len(grid[0])
        h = len(grid)
        
        is_centered_x = abs(self.x - cx) <= self.speed * 0.50
        is_centered_y = abs(self.y - cy) <= self.speed * 0.50
        
        # pacpos_rounded = (round(pacposition[0]), round(pacposition[1]))
        px, py = self._ghost_chase(grid, pacpos, pacdirection)
        path = self.find_path((cx, cy), (px, py), grid)
        if len(path) > 1 and is_centered_x and is_centered_y:
            self._set_direction(path[1], cx, cy)

        next_x, next_y = self._update_position(w, h)

        acx, acy = cx, cy
        if self.direction == Direction.UP:
            acy = (acy - 1) % h
        elif self.direction == Direction.DOWN:
            acy = (acy + 1) % h
        elif self.direction == Direction.LEFT:
            acx = (acx - 1) % w
        elif self.direction == Direction.RIGHT:
            acx = (acx + 1) % w

        if grid[acy][acx] == Tile.WALL:
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
        return img

    def update(self) -> None:
        self.anim_frame += 0.1
        self.frame = int(self.anim_frame) % self.nb_frames