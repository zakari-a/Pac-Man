import pygame
# from config.config import load_config
import sys
import random
import json

from maze.maze_adapter import MazeAdapter, Tile
from assets.assetmanager import AssetManager, GhostType
from renderer.renderer import Renderer
from config.config import Config, load_config
from entities.entities import Pacman, Ghost, PacState
from game_view.ui import Menu, Instructions, HighScores, GameState, Paused
from game_view.banners import Banners


class Game():

    def __init__(self, configs: Config) -> None:
        self.configs = configs

        # pygame variables
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
        self.dt = 0.0

        # ui
        self.assets: AssetManager
        self.menu: Menu
        self.inst: Instructions
        self.hs: HighScores
        self.pause: Paused
        self.banners: Banners

        # maze and render variables
        self.adapter: MazeAdapter
        self.renderer: Renderer
        self.grid: list[list[Tile]] = []
        self.tile_size = 0
        self.pacman: Pacman
        self.ghosts: list[Ghost]

        # levels variables
        self.level_num = 0
        self.max_level = 10
        self.levels = self.configs.levels
        self.done = False
        self.level_timer: float = self.configs.level_max_time

        # key variables
        self.last_move_time = 0
        self.move_cooldown = 50
        self.last_check = 0

        # highscors variables
        try:
            with open("highscores.json", "r") as f:
                self.highscores = json.load(f)
        except json.JSONDecodeError:
            self.highscores = []
        self.h_s = self.highscores[0]["score"] if self.highscores else 0

        # player variables
        self.game_state: GameState = GameState.MENU
        self.score = 0
        self.lives = self.configs.lives
        self.pacgum_points = configs.points_per_pacgum
        self.supergum_points = configs.points_per_super_pacgum
        self.corners: list[tuple[int, int]] = []
        self._init_level()

        # cheat mode
        self.invincible = False
        self.freeze = False
        self.super_speed = False
        self.stop_time = False

    def _init_level(self) -> None:
        if self.level_num == len(self.levels):
            self.game_state = GameState.GAME_OVER
            self.done = True
            return

        self.invincible = False
        self.freeze = False
        self.super_speed = False
        self.stop_time = False
        self.level_timer = self.configs.level_max_time
        level = self.levels[self.level_num]
        if self.level_num != 0:
            self.configs.seed = random.randint(1, 9999)

        self.adapter = MazeAdapter(level.width,
                                   level.height, self.configs.seed)
        self.grid = self.adapter.load(self.configs.pacgum)

        rows = len(self.grid)
        cols = len(self.grid[0])

        self.tile_size = min(self.width // cols, self.height // rows)
        self.assets = AssetManager(self.tile_size)
        self.assets.load()

        self.renderer = Renderer(self.screen, self.assets, self.grid)
        self.renderer._set_offset()
        self.corners = self.renderer._get_corners()

        types = [GhostType.RED, GhostType.BLUE,
                 GhostType.PINK, GhostType.ORANGE]
        self.ghosts = [
            Ghost(types[i], self.corners[i], self.grid, self.assets)
            for i in range(len(types))
            ]

        self.menu = Menu(self.assets, self.screen)
        self.inst = Instructions(self.assets, self.screen)
        self.hs = HighScores(
            self.assets, self.screen, self.highscores,
            self.configs.highscore_filename)
        self.pause = Paused(self.assets, self.screen)
        self.banners = Banners(self.assets, self.screen, self.renderer)

        self.pacman = Pacman(self.tile_size, self.grid, self.assets)
        self.pacman._find_spawn()
        for ghost in self.ghosts:
            ghost._reset()

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.menu.index = (self.menu.index - 1) % len(self.menu.menu_list)
        elif event.key == pygame.K_DOWN:
            self.menu.index = (self.menu.index + 1) % len(self.menu.menu_list)

        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.menu.menu_list[self.menu.index][1]
            if self.game_state == GameState.PLAYING:
                self._init_level()

    def _handle_play_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        self.pacman._set_pacmouvements(event.key)
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.PAUSED

        elif event.key == pygame.K_F1:
            self.invincible = not self.invincible
        elif event.key == pygame.K_F2:
            self.level_num += 1
            self.score += self.configs.pacgum * self.pacgum_points
            self._init_level()
        elif event.key == pygame.K_F3:
            self.freeze = not self.freeze
        elif event.key == pygame.K_F4:
            if self.lives < 7:
                self.lives += 1
        elif event.key == pygame.K_F5:
            self.super_speed = not self.super_speed
            if self.super_speed:
                self.pacman.speed = max(1, round(self.tile_size / 5))
            else:
                self.pacman.speed = max(1, round(self.tile_size / 8))
        elif event.key == pygame.K_F6:
            self.stop_time = not self.stop_time

    def _handle_inst_input(self, event: pygame.event.Event) -> None:
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_LEFT:
            self.inst.index = (self.inst.index - 1) % len(self.inst.sections)
        elif event.key == pygame.K_RIGHT:
            self.inst.index = (self.inst.index + 1) % len(self.inst.sections)
        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.inst.buttons[self.inst.index][1]
        elif event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU

    def _handle_pause_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.pause.index = (self.pause.index - 1) % len(self.pause.list)
        elif event.key == pygame.K_DOWN:
            self.pause.index = (self.pause.index + 1) % len(self.pause.list)

        elif event.key == pygame.K_RETURN:
            self.game_state = self.pause.paused_list[self.pause.index][1]
            if self.game_state == GameState.MENU:
                self.level_num = 0
                self.score = 0
                self.lives = self.configs.lives

    def _handle_hs_input(self, event: pygame.event.Event) -> None:
        now = pygame.time.get_ticks()
        if event.type != pygame.KEYDOWN:
            return

        index = self.hs.index
        if event.key == pygame.K_LEFT:
            self.hs.index = (index - 1) % len(self.hs.buttons)
        elif event.key == pygame.K_RIGHT:
            self.hs.index = (index + 1) % len(self.hs.buttons)
        elif event.key == pygame.K_RETURN:
            if now - self.last_move_time < self.move_cooldown:
                return
            self.last_move_time = now
            self.game_state = self.hs.buttons[self.hs.index][1]
        elif event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU

    def _handle_score_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.hs.index = (self.hs.index - 1) % 2

        elif event.key == pygame.K_DOWN:
            self.hs.index = (self.hs.index + 1) % 2

        if self.hs.index == 0:
            if (event.key == pygame.K_BACKSPACE
                    and self.hs.name_index >= 0):
                self.hs.name[self.hs.name_index] = "_"
                if self.hs.name_index == 0:
                    return
                self.hs.name_index -= 1

            elif ((event.unicode.isalnum() or event.unicode == " ")
                  and self.hs.name_index <= 9):
                index = self.hs.name_index
                self.hs.name[index] = event.unicode
                if self.hs.name_index == 9:
                    return
                self.hs.name_index += 1
        else:
            if event.key == pygame.K_RETURN:
                self.game_state = GameState.MENU
                self.hs._update_highsocores(self.score)
                self.level_num = 0
                self.score = 0

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
        texts = ["SCORE:", f"{self.score}",
                 "LIVES:", f"{self.lives}",
                 "HIGHSCORE:", f"{self.hs.highscore}",
                 "TIME:", f"{int(self.level_timer)}"]
        if not self.stop_time:
            self.level_timer -= self.dt
        for i, text in enumerate(texts):
            if i == 4:
                spacing = 0.10
                start_x = self.width * 0.80
                start_y = self.height * spacing

            label_surfacee = self.assets.font_20.render(text, True, "white")
            self.screen.blit(label_surfacee, (start_x, start_y))
            spacing += 0.05
            if (spacing * 10) % 2 == 0:
                spacing += 0.05
            start_y = self.height * spacing

    def _play(self) -> None:
        if self.level_timer <= 0:
            self.game_state = GameState.GAME_OVER
            self.done = False

        self.screen.fill("black")
        self.renderer._draw_maze()
        self._game_stats()
        if self._check_empty_grid():
            self.level_num += 1
            self._init_level()
        if self.pacman.mode == PacState.ALIVE:
            for ghost in self.ghosts:
                ghost._update_state(self.pacman)
            collision, pos = self.pacman.check_collision(self.ghosts, self.invincible)
            if collision == 1:
                if not self.invincible:
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
                self.score += self.pacman.eat(self.ghosts,
                                              self.pacgum_points,
                                              self.supergum_points)
                self.pacman._go_normal()
            self.renderer._draw_pacman(self.pacman)
            self.renderer._draw_ghosts(
                self.ghosts, self.pacman,
                self.ghosts[0].position, self.freeze)

        elif self.pacman.mode == PacState.DYING:
            self.renderer._draw_pacman_death(self.pacman)
            for ghost in self.ghosts:
                ghost._reset()
            self.pacman.mode = PacState.ALIVE
            self.renderer.mod = len(self.assets.pacman)
            self.pacman._reset()
            self.lives -= 1
            if self.lives == 0:
                self.game_state = GameState.GAME_OVER
                self.lives = self.configs.lives

    def run(self) -> None:
        while self.running:
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
                self.screen.blit(self.menu.background, (0, 0))
                self.menu.run()

            elif self.game_state == GameState.PLAYING:
                self._play()

            elif self.game_state == GameState.HIGHSCORES:
                self.screen.blit(self.hs.background, (0, 0))
                self.hs.run()

            elif self.game_state == GameState.INSTRUCTIONS:
                self.screen.blit(self.inst.background, (0, 0))
                self.inst.run()

            elif self.game_state == GameState.EXIT:
                self.running = False

            elif self.game_state == GameState.PAUSED:
                self.renderer._draw_maze()
                self.pause.run()

            elif self.game_state == GameState.GAME_OVER:
                if self.banners._game_over(self.done):
                    self.game_state = GameState.FINISHED

            elif self.game_state == GameState.VICTORY:
                if self.banners._victory(self.score):
                    self.game_state = GameState.PLAYING

            elif self.game_state == GameState.FINISHED:
                self.screen.blit(self.hs.background, (0, 0))
                self.hs.enter_name(self.done, self.score)

            self.dt = self.clock.tick(60) / 1000
            pygame.display.flip()


if __name__ == "__main__":
    configs = load_config(sys.argv[-1])
    game = Game(configs)
    game.run()
