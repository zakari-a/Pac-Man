import pygame
from enum import Enum
from config.config import load_config
import sys
import random
import json
import math
import time

from maze.maze_adapter import MazeAdapter, Tile
from assets.assetmanager import AssetManager, GhostType
from renderer.renderer import Renderer
from entities.entities import Pacman, Ghost, PacState

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4
    HIGHSCORES = 5
    INSTRUCTIONS = 6
    FINISHED = 7
    EXIT = 9

class GameEngine():

    def __init__(self, configs) -> None:

        self.configs = configs
        pygame.init()
        pygame.key.set_repeat()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.SCALED)
        pygame.display.set_caption("Pac-Man")
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()
        self.frame_tick = 0
        self.counter = 0
        self.dt = 0

        self.assets = None
        # self.assets.load()

        # menu variables
        self.game_state: GameState = GameState.MENU
        self.adapter: MazeAdapter = None
        self.menu_font = None
        self.menu_list = [
            ("START GAME", GameState.PLAYING),
            ("INSTRUCTIONS", GameState.INSTRUCTIONS),
            ("HIGHSCORES", GameState.HIGHSCORES),
            ("EXIT", GameState.EXIT)
            ]
        self.menu_index = 0
        commands_background = pygame.image.load("src/assets/commands_background.jpeg").convert()
        background = pygame.image.load("src/assets/new_pacman_menu.png").convert()
        self.menu_background = pygame.transform.scale(background, (self.screen.get_size()))
        self.commands_background = pygame.transform.scale(commands_background, (self.screen.get_size()))

        # maze and render variables
        self.renderer = None
        self.adapter = None
        self.grid = []
        self.tile_size = 0
        self.pacman = None
        self.ghosts = None

        # levels variables
        self.level_num = 0
        self.max_level = 10
        self.levels = self.configs.levels
        self.done = False
        self.level_timer = self.configs.level_max_time


        # pause variables
        self.paused_list = [("RESUME", GameState.PLAYING) , ("EXIT TO MAIN MENU", GameState.MENU)]
        self.pause_index = 0

        # instructions variables
        self.instuctions_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 35)
        self.inst_parts_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 20)
        self.commands_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 10)
        self.inst_parts = ["MOVEMENTS AND NAVIGATION :", "CHEATS :"]
        self.movement_text = [
            "ARROWS: TO MOVE AND NAVIGATE",
            "W A S D: TO MOVE AND NAVIGATE",
            "ESCAPE: TO PAUSE THE GAME"
        ]
        
        self.cheats_text = [
            "  NOT READY",
            "  NOT READY",
            "  NOT READY",
            "  NOT READY",
            "  NOT READY",
            "  NOT READY"
        ]
        self.inst_index = 0
        self.instruction_guids = [("EXIT TO MAIN MENU", GameState.MENU), ("HIGHSCORES", GameState.HIGHSCORES)]
        self.last_move_time = 0
        self.move_cooldown = 50
        self.last_check = 0
        self.hs_index = 0


        # highscors variables
        with open("highscores.json", "r") as f:
            self.highscores = json.load(f)
        self.hs_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 10)
        self.hs_guids = [("EXIT TO MAIN MENU", GameState.MENU), ("INSTRUCTIONS", GameState.INSTRUCTIONS)]
        self.name = ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]
        self.hs_index = 0
        self.name_index = 0
        self.hs = self.highscores[0]["score"]
    

        # player variables
        self.score = 0
        self.lives = self.configs.lives
        self.pacgum_points = configs.points_per_pacgum
        self.supergum_points = configs.points_per_super_pacgum
        self.corners = []
        self._init_level()

        # banner vars
        self.scale = 0.4
        self.shrink_x = 1
        self.shrink_y = 2
        self.target_width = self.width * self.shrink_x
        self.target_height = self.height / self.shrink_y

        
    def _init_level(self) -> None:
        if self.level_num >= len(self.levels):
            self.game_state = GameState.FINISHED
            self.done = False
            return
        self.level_timer = self.configs.level_max_time
        level = self.levels[self.level_num]
        if level != 1:
            self.configs.seed = random.randint(1, 9999)
        self.adapter = MazeAdapter(level.width, level.height, self.configs.seed)
        self.grid = self.adapter.load()
        
        rows = len(self.grid)
        cols = len(self.grid[0])

        self.tile_size = min(self.width // cols, self.height // rows)
        self.assets = AssetManager(self.tile_size)
        self.assets.load()
        self.menu_font = self.assets.font

        self.renderer = Renderer(self.screen, self.assets, self.grid)
        self.renderer._set_offset()
        self.corners = self.renderer._get_corners()

        types = [GhostType.RED,GhostType.BLUE,
                 GhostType.PINK, GhostType.ORANGE]
        self.ghosts = [
            Ghost(types[i], self.corners[i], self.grid,
            self.assets) for i in range(len(types))]
        
        
        self.pacman = Pacman(self.tile_size, self.grid, self.assets)
        self.pacman._find_spawn()
        for ghost in self.ghosts:
            ghost._reset()

    
    def _menu(self) -> None: 
        self.lives = self.configs.lives
        spacing = 0.50
        start_x = self.width * 0.10
        start_y = self.height * spacing        
        for i, (label, state) in enumerate(self.menu_list):
            color = "white"
            if i == self.menu_index:
                color = "yellow"
                label = f"→ {label}"
            label_surfacee = self.menu_font.render(label, True, color)
            self.screen.blit(label_surfacee, (start_x, start_y))
            spacing += 0.07
            start_y = self.height * spacing


    def _handle_menu_input(self, event: pygame.event) -> None:
        # if event in (pygame.K_UP, pygame.K_DOWN):
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.menu_index = (self.menu_index - 1) % len(self.menu_list)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.menu_index = (self.menu_index + 1) % len(self.menu_list)
        
        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.menu_list[self.menu_index][1]
            if self.game_state == GameState.PLAYING:
                self._init_level()


    def _handle_play_input(self, event: pygame.event) -> None:
        if event.type != pygame.KEYDOWN:
            return 
        
        self.pacman._set_pacmouvements(event.key)
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.PAUSED

    def _handle_inst_input(self, event: pygame.event) -> None:
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return
        
        if event.key == pygame.K_LEFT:
            self.inst_index = (self.inst_index - 1) % len(self.instruction_guids)
        elif event.key == pygame.K_RIGHT:
            self.inst_index = (self.inst_index + 1) % len(self.instruction_guids)
        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.instruction_guids[self.inst_index][1]
        elif event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
            

    def _handle_pause_input(self, event: pygame.event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.pause_index = (self.pause_index - 1) % len(self.paused_list)
        elif event.key == pygame.K_DOWN:
            self.pause_index = (self.pause_index + 1) % len(self.paused_list)
        
        elif event.key == pygame.K_RETURN:
            self.game_state = self.paused_list[self.pause_index][1]

    def _handle_hs_input(self, event: pygame.event) -> None:
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return 
        
        if event.key == pygame.K_LEFT:
            self.hs_index = (self.hs_index - 1) % len(self.hs_guids)
        elif event.key == pygame.K_RIGHT:
            self.hs_index = (self.hs_index + 1) % len(self.hs_guids)
        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.hs_guids[self.hs_index][1]
        elif event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU

    def _handle_score_input(self, event: pygame.event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        if event.key == pygame.K_UP:
            self.hs_index = (self.hs_index - 1) % 2
        
        elif event.key == pygame.K_DOWN:
            self.hs_index = (self.hs_index + 1) % 2
        
        if self.hs_index == 0:
            if event.key == pygame.K_BACKSPACE and self.name_index >= 0:
                self.name[self.name_index] = "_"
                if self.name_index == 0:
                    return
                self.name_index -= 1

            elif (event.unicode.isalnum() or event.unicode == " " ) and self.name_index <= 9:
                self.name[self.name_index] = event.unicode
                if self.name_index == 9:
                    return
                self.name_index += 1
        else:
            if event.key == pygame.K_RETURN:
                self.game_state = GameState.MENU
                self._update_highsocores()

        
    def _paused(self) -> None:
        # self.screen.fill("black")
        self.renderer._draw_maze()
        self.renderer._draw_pacman(self.pacman)
        # for ghost in self.ghosts:
        self.renderer._draw_ghosts(self.ghosts, self.pacman, self.ghosts[0].position)
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        start_x = self.width * 0.30
        start_y = self.height * 0.15
        box_width = self.width * 0.35
        box_height = self.height * 0.13
        spacing = self.height * 0.05

        for i, (label, state) in enumerate(self.paused_list):
            box_rect = pygame.Rect(start_x, start_y + i * (box_height + spacing),
                            box_width, box_height)
            color = "darkblue"
            if i == self.pause_index:
                color = "white"
                label = f"→ {label}"
                
            pygame.draw.rect(self.screen, "black", box_rect)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.menu_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)

    def _eat(self):
        x = self.pacman.position[0] + self.pacman.pac_size // 2
        y = self.pacman.position[1] + self.pacman.pac_size // 2
        gx = x // self.tile_size
        gy = y // self.tile_size
        char = self.grid[gy][gx]
        if char in [Tile.PACGUM, Tile.SUPER_PACGUM]:
            self.grid[gy][gx] = Tile.EMPTY
            if char == Tile.PACGUM:
                self.score += self.pacgum_points
            elif char == Tile.SUPER_PACGUM:
                self.score += self.supergum_points
            
    def _check_empty_grid(self) -> bool:
        for row in self.grid:
            for tile in row:
                if tile == Tile.PACGUM or tile == Tile.SUPER_PACGUM:
                    return False
        self.game_state = GameState.VICTORY
        return True    


    def _game_stats(self) -> None:
        spacing = 0.10
        start_x = self.width * 0.05
        start_y = self.height * spacing
        self.level_timer -= self.dt
        texts = ["SCORE:", f"{self.score}",
                 "LIVES:", f"{self.lives}",
                 "HIGHSCORE:", f"{self.hs}",
                 "TIME:", f"{int(self.level_timer)}"]
        for i, text in enumerate(texts):
            if i == 4:
                spacing = 0.10
                start_x = self.width * 0.80
                start_y = self.height * spacing

            label_surfacee = self.menu_font.render(text, True, "white")
            self.screen.blit(label_surfacee, (start_x, start_y))
            spacing += 0.05
            if (spacing * 10) % 2 == 0:
                spacing += 0.05
            start_y = self.height * spacing

    def _victory(self) -> None:
        self._move_frame()
        self.renderer._draw_maze()
        banner = self.assets.victory
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 170), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (0, 0))
        center_x, center_y = self.screen.get_rect().center
        if self.counter < 7:
            if self.shrink_x > 0.6 and self.shrink_y < 5.5:
                self.shrink_x -= 0.01
                self.shrink_y += 0.08
                self.target_width = self.width * self.shrink_x
                self.target_height = self.height / self.shrink_y

            banner = pygame.transform.smoothscale(banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(banner, banner_rect)
            if self.shrink_x <= 0.6:
                labels = [
                    ("YOUR CURRENT SCORE IS:", self.menu_font),
                    (f"{self.score}", self.instuctions_font),
                    ("NEXT LEVEL WILL START IN:", self.menu_font),
                    (f"{7 - self.counter}", self.instuctions_font)
                ]

                pos = [-75, -0, 75, 150]
                for i, (key, value) in enumerate(labels):
                    label = value.render(key, True, "white")
                    label_rect = label.get_rect(center=(center_x , center_y + pos[i]))
                    self.screen.blit(label, label_rect)
    
        if self.counter == 7:
            banner = pygame.transform.smoothscale(banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)
            self.game_state = GameState.PLAYING
            self.shrink_x = 1
            self.shrink_y = 2
            self.counter = 0
        

    def _play(self) -> None:
        if self.level_timer == 0:
            self.game_state = GameState.FINISHED
            self.done = False

        self.screen.fill("black")
        self.renderer._draw_maze()
        # self.renderer._draw_pacman(self.pacman)
        # self.renderer._draw_ghosts(self.ghosts, self.pacman, self.ghosts[0].position)
        self._game_stats()
        if self._check_empty_grid():
            self.level_num += 1
            self._init_level()
            
        if self.pacman.mode == PacState.ALIVE:
            self._eat()
            for ghost in self.ghosts:
                ghost._update_state(self.pacman)
            collision, pos = self.pacman.check_collision(self.ghosts)
            if collision == 1:
                self.pacman.death_start = pygame.time.get_ticks()
                self.pacman.mode = PacState.DYING

            elif collision == 2:
                found = None
                for ghost in self.ghosts:
                    if ghost.position == pos:
                        found = ghost
                if found:
                    found.alive = False
                    found.position = found.base_corner
                    found.counter = 0
                    found.was_dead = 1
                    found.death_start = pygame.time.get_ticks()
                self.score += self.configs.points_per_ghost

            else:
                self.pacman._update_pacposition()
                self.pacman.eat(self.ghosts)
                self.pacman._go_normal()
            self.renderer._draw_pacman(self.pacman)
            self.renderer._draw_ghosts(self.ghosts, self.pacman, self.ghosts[0].position)

        elif self.pacman.mode == PacState.DYING:
            # print("here")
            self.renderer._draw_pacman_death(self.pacman)
            for ghost in self.ghosts:
                ghost._reset()
            self.pacman.mode = PacState.ALIVE
            self.renderer._draw_pacman(self.pacman)
            self.renderer.mod = len(self.assets.pacman)
            self.pacman._reset()
            self.lives -= 1
            if self.lives == 0:
                self.game_state = GameState.GAME_OVER


    def _draw_sections(self) -> None:
        start_x = self.width * 0.12
        start_y = self.height * 0.20
        for text in self.inst_parts:
            label_surface = self.inst_parts_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            start_x = self.width * 0.68

    def _draw_keys(self) -> None:
        coords = [
            (self.width * 0.15, self.height * 0.30),
            (self.width * 0.11, self.height * 0.36),
            (self.width * 0.15, self.height * 0.36),
            (self.width * 0.19, self.height * 0.36)
        ]
        keys = ["↑", "←", "↓", "→"]

        width = self.width * 0.03
        height = self.height * 0.05
        for i, coord in enumerate(coords):
            box_rect = pygame.Rect(coord[0], coord[1], width, height)
            pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
            label_surface = self.commands_font.render(keys[i], True, "white")
            label_rect = label_surface.get_rect(center=box_rect.center)
            self.screen.blit(label_surface, label_rect)
        
        coords = [
            (self.width * 0.15, self.height * 0.45),
            (self.width * 0.11, self.height * 0.51),
            (self.width * 0.15, self.height * 0.51),
            (self.width * 0.19, self.height * 0.51)
        ]
        keys = ["W", "A", "S", "D"]

        for i, coord in enumerate(coords):
            box_rect = pygame.Rect(coord[0], coord[1], width, height)
            pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
            label_surface = self.commands_font.render(keys[i], True, "white")
            label_rect = label_surface.get_rect(center=box_rect.center)
            self.screen.blit(label_surface, label_rect)
        
        box_rect = pygame.Rect(self.width * 0.125, self.height * 0.63, self.width * 0.08, self.height * 0.05)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
        label_surface = self.commands_font.render("ESCAPE", True, "white")
        label_rect = label_surface.get_rect(center=box_rect.center)
        self.screen.blit(label_surface, label_rect)


        spacing = 10
        start_x = self.width * 0.60
        start_y = self.height * 0.30
        keys = ["F1", "F2", "F3", "F4", "F5", "F6"]
        for i in range(len(keys)):
            box_rect = pygame.Rect(start_x, start_y + i * (height + spacing),
                                   width, height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=5)
            pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
            label_surface = self.commands_font.render(keys[i], True, "white")
            label_rect = label_surface.get_rect(center=box_rect.center)
            self.screen.blit(label_surface, label_rect)
        
        

    def _draw_inst_text(self) -> None:
        coords = [
            (self.width * 0.25, self.height * 0.36),
            (self.width * 0.25, self.height * 0.51),
            (self.width * 0.25, self.height * 0.65),
        ]

        for i, text in enumerate(self.movement_text):
            label_surface = self.commands_font.render(text, True, "white")
            self.screen.blit(label_surface, coords[i])
        
        spacing = 0.312
        start_x = self.width * 0.68
        start_y = self.height * spacing
        for text in self.cheats_text:
            label_surface = self.commands_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.067
            start_y = self.height * spacing

    def _instructions(self) -> None:
        # self.screen.fill("black")
        label_surface = self.instuctions_font.render("INSTRUCTION", True, "yellow")
        label_surface2 = self.instuctions_font.render("___________", True, "darkblue")
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (self.width * 0.02, self.height * 0.02))
        # pygame.draw.rect(self.screen, "gray48", box_rect, border_radius=50)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=50)
        self.screen.blit(label_surface, (self.width * 0.35, self.height * 0.10))
        self.screen.blit(label_surface2, (self.width * 0.35, self.height * 0.12))

        self._draw_sections()
        self._draw_inst_text()
        self._draw_keys()


        x = self.width * 0.02
        y = self.height * 0.9
        box_width = self.width * 0.20
        box_height = self.height * 0.08


        for i, (label, state) in enumerate(self.instruction_guids):
            color = "darkblue"
            if i == self.inst_index:
                color = "white"
                label = f"→ {label}"
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.commands_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78

    def _update_highsocores(self) -> None:
        name = "".join(self.name).rstrip("_")
        self.highscores.append({"name": name, "score": self.score})
        self.highscores = sorted(self.highscores, key=lambda value: value["score"], reverse=True)[:10]

        with open("highscores.json", "w") as f:
            json.dump(self.highscores, f, indent=2)

    def _highscores(self) -> None:
        # self.screen.fill("black")
        label_surface = self.instuctions_font.render("HIGHSCORES", True, "yellow")
        label_surface2 = self.instuctions_font.render("__________", True, "darkblue")
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (self.width * 0.02, self.height * 0.02))
        # pygame.draw.rect(self.screen, "gray48", box_rect, border_radius=20)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=50)
        self.screen.blit(label_surface2, (self.width * 0.35, self.height * 0.12))
        self.screen.blit(label_surface, (self.width * 0.35, self.height * 0.10))

        spacing = 0.25
        start_x = self.width * 0.12
        start_y = self.height * spacing
        for i, highscore in enumerate(self.highscores):
            text = f"→ {highscore["name"].upper()} : {highscore["score"]}"
            label_surface = self.hs_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.08
            start_y = self.height * spacing
            if start_y >= self.height * 0.8:
                spacing = 0.25
                start_y = self.height * spacing
                start_x = self.width * 0.60

        x = self.width * 0.02
        y = self.height * 0.9
        box_width = self.width * 0.20
        box_height = self.height * 0.08
        for i, (label, state) in enumerate(self.hs_guids):
            color = "darkblue"
            if i == self.hs_index:
                color = "white"
                label = f"→ {label}"
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.commands_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78

    def _move_frame(self):
        c_time = pygame.time.get_ticks()
        if c_time - self.frame_tick >= 1000:
            self.counter += 1
            self.frame_tick = pygame.time.get_ticks()


    def _game_over(self) -> None:
        self._move_frame()
        banner = self.assets.game_over
        if self.done:
            banner = self.assets.finish
        self.renderer._draw_maze()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 170), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (0, 0))
        # target_width = self.width * 0.4
        # target_height = self.height / 5.5
        center_x, center_y = self.screen.get_rect().center
        if self.counter < 4:
            if self.shrink_x > 0.6 and self.shrink_y < 5.5:
                self.shrink_x -= 0.01
                self.shrink_y += 0.08
                self.target_width = self.width * self.shrink_x
                self.target_height = self.height / self.shrink_y

            banner = pygame.transform.smoothscale(banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)
    
        if self.counter == 4:
            banner = pygame.transform.smoothscale(banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)
            self.game_state = GameState.FINISHED
            self.shrink_x = 1
            self.shrink_y = 2
            self.counter = 0


    def _finished(self) -> None:
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (self.width * 0.02, self.height * 0.02))
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=50)
        message = "WELL DONE!" if self.done else "UNLUCKY"
        label_surface1 = self.instuctions_font.render(message, True, "white")
        label_surface2 = self.hs_font.render("ENTER YOUR NAME", True, "white")
        label_surface3 = self.hs_font.render("YOUR SCORE IS:", True, "white")
        label_surface4 = self.instuctions_font.render(f"{self.score}", True, "yellow")
        label_rect = label_surface4.get_rect(center=box_rect.center)
        self.screen.blit(label_surface1, (self.width * 0.40, self.height * 0.15))
        self.screen.blit(label_surface3, (self.width * 0.44, self.height * 0.25))
        self.screen.blit(label_surface4, label_rect)
        self.screen.blit(label_surface2, (self.width * 0.44, self.height * 0.60))
        spacing = 0.375
        start_x = self.width * spacing
        start_y = self.height * 0.70

        for i, char in enumerate(self.name):
            color = "white"
            if i == self.name_index:
                color = "yellow"
            label_surface = self.menu_font.render(char, True, color)
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.025
            start_x = self.width * spacing

        x = self.width * 0.02
        y = self.height * 0.9
        box_width = self.width * 0.20
        box_height = self.height * 0.08
        text = "CONFIRM"
        color = "darkblue"
        if self.hs_index == 1:
            color = "white"
            text = f"→ {text}"
        box_rect = pygame.Rect(x, y, box_width, box_height)
        pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
        label = self.commands_font.render(text, True, "white")
        label_rect = label.get_rect(center=box_rect.center)
        self.screen.blit(label, label_rect)



    def run(self) -> None:
        while self.running:
        #     print(self.game_state)
        #     print(self.menu_index)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                if self.game_state == GameState.MENU:
                    self._handle_menu_input(event)
                if self.game_state == GameState.PLAYING:
                    self._handle_play_input(event)
                if self.game_state == GameState.PAUSED:
                    self._handle_pause_input(event)
                if self.game_state == GameState.INSTRUCTIONS:
                    self._handle_inst_input(event)
                if self.game_state == GameState.HIGHSCORES:
                    self._handle_hs_input(event)
                if self.game_state == GameState.FINISHED:
                    self._handle_score_input(event)

            if self.game_state == GameState.MENU:
                self.screen.blit(self.menu_background, (0, 0))
                # self.screen.fill("black")
                self._menu()

            elif self.game_state == GameState.PLAYING:
                self._play()

            elif self.game_state == GameState.HIGHSCORES:
                self.screen.blit(self.commands_background, (0, 0))
                self._highscores()
            
            elif self.game_state == GameState.INSTRUCTIONS:
                self.screen.blit(self.commands_background, (0, 0))
                self._instructions()

            elif self.game_state == GameState.EXIT:
                self.running = False

            elif self.game_state == GameState.PAUSED:
                self._paused()
                # for event in pygame.event.get():
                    # self._handle_paused_input()
            elif self.game_state == GameState.GAME_OVER:
                self._game_over()

            elif self.game_state == GameState.VICTORY:
                self._victory()

            elif self.game_state == GameState.FINISHED:
                self.screen.blit(self.commands_background, (0, 0))
                self._finished()

            # self.clock.tick(60)
            self.dt = self.clock.tick(60) / 1000
            pygame.display.flip()
        

if __name__=="__main__":
    configs = load_config(sys.argv[-1])
    game = GameEngine(configs)
    game.run()
