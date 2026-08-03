import pygame
from enum import Enum
from config.config import load_config
import sys
import random
import json

from maze.maze_adapter import MazeAdapter
from assets.assetmanager import AssetManager, GhostType
from renderer.renderer import Renderer
from entities.entities import Pacman, Ghost

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4
    HIGHSCORES = 5
    INSTRUCTIONS = 6
    EXIT = 7

class GameEngine():

    def __init__(self, configs) -> None:

        self.configs = configs
        pygame.init()
        pygame.key.set_repeat()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Pac-Man")
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()

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
            ("EXIT", GameState.EXIT)]
        self.menu_index = 0
        background = pygame.image.load("src/assets/new_pacman_menu.png").convert()
        self.menu_background = pygame.transform.scale(background, (self.width, self.height))  

        # maze and render variables
        self.renderer = None
        self.adapter = None
        self.grid = []
        self.tile_size = 0
        self.pacman = None
        self.ghosts = None

        # levels variables
        self.level_num = 1
        self.max_level = 10
        self.levels = self.configs.levels
        self._init_level()


        # pause variables
        self.paused_list = [("RESUME", GameState.PLAYING) , ("EXIT TO MAIN MENU", GameState.MENU)]
        self.pause_index = 0

        # instructions variables
        self.instuctions_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 35)
        self.inst_parts_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 20)
        self.commands_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 10)
        self.inst_parts = ["MOVEMENTS AND NAVIGATION :", "CHEATS :"]
        self.movement_text = [
            "- W OR UP-KEY : TO MOVE UP",
            "- S OR DOWN-KEY : TO MOVE DOWN",
            "- D OR RIGHT-KEY : TO MOVE RIGHT",
            "- A OR LEFT-KEY : TO MOVE LEFT",
            "- ESCAPE: TO PAUSE THE GAME",
            "- S AND W : TO UP AND DOWN NAVIGATE IN MENU"]
        
        self.cheats_text = [
            "- F1 : NOT READY",
            "- F2 : NOT READY",
            "- F3 : NOT READY",
            "- F4 : NOT READY",
            "- F5 : NOT READY",
            "- F6 : NOT READY"
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
        # print(self.highscores)
        self.hs_font = pygame.font.Font("src/assets/PressStart2P-Regular.ttf", 10)
        self.hs_guids = [("EXIT TO MAIN MENU", GameState.MENU), ("INSTRUCTIONS", GameState.INSTRUCTIONS)]
        
    def _init_level(self) -> None:
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
        corners = self.renderer._get_corners()

        types = [GhostType.RED,GhostType.BLUE,
                 GhostType.PINK, GhostType.ORANGE]
        self.ghosts = [
            Ghost(types[i], corners[i], self.grid,
            self.tile_size) for i in range(len(types))]
        
        self.pacman = Pacman(self.tile_size, self.grid)
        self.pacman._find_spawn()
    
    def _menu(self) -> None:
        # self.screen.fill("black")
        # self.screen.blit(self.menu_background, (0, 0))       
        start_x = self.width * 0.60
        start_y = self.height * 0.20
        box_width = self.width * 0.35
        box_height = self.height * 0.13
        spacing = self.height * 0.05
        
        colors = ["cyan", "yellow", "purple", "red"]
        for i, (label, state) in enumerate(self.menu_list):
            box_rect = pygame.Rect(start_x, start_y + i * (box_height + spacing),
                                   box_width, box_height)
            color = colors[i]
            if i == self.menu_index:
                color = "white"
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.menu_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)


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
        
    def _paused(self) -> None:
        self.screen.fill("black")
        self.renderer._draw_maze()
        self.renderer._draw_pacman(self.pacman, 0)
        for ghost in self.ghosts:
            self.renderer._draw_ghosts(ghost)
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
            pygame.draw.rect(self.screen, "black", box_rect)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.menu_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)


    def _play(self) -> None:
        self.pacman._update_pacposition()
        self.screen.fill("black")
        self.renderer.run(self.pacman, self.ghosts)


    def _draw_sections(self) -> None:
        start_x = self.width * 0.12
        start_y = self.height * 0.30
        for text in self.inst_parts:
            label_surface = self.inst_parts_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            start_x = self.width * 0.68

    def _draw_inst_text(self) -> None:
        spacing = 0.37
        start_x = self.width * 0.12
        start_y = self.height * spacing
        for text in self.movement_text:
            label_surface = self.commands_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.05
            start_y = self.height * spacing
        
        spacing = 0.37
        start_x = self.width * 0.68
        start_y = self.height * spacing
        for text in self.cheats_text:
            label_surface = self.commands_font.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.05
            start_y = self.height * spacing

    def _instructions(self) -> None:
        # self.screen.fill("black")
        label_surface = self.instuctions_font.render("INSTRUCTION", True, "yellow")
        label_surface2 = self.instuctions_font.render("___________", True, "darkblue")
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        pygame.draw.rect(self.screen, "gray48", box_rect, border_radius=50)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=50)
        self.screen.blit(label_surface, (self.width * 0.35, self.height * 0.10))
        self.screen.blit(label_surface2, (self.width * 0.35, self.height * 0.12))

        self._draw_sections()
        self._draw_inst_text()

        x = self.width * 0.02
        y = self.height * 0.9
        box_width = self.width * 0.20
        box_height = self.height * 0.08

        for i, (label, state) in enumerate(self.instruction_guids):
            color = "darkblue"
            if i == self.inst_index:
                color = "white"
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.commands_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78

    def _highscores(self) -> None:
        # self.screen.fill("black")
        label_surface = self.instuctions_font.render("HIGHSCORES", True, "yellow")
        label_surface2 = self.instuctions_font.render("__________", True, "darkblue")
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        pygame.draw.rect(self.screen, "gray48", box_rect, border_radius=20)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=20)
        self.screen.blit(label_surface2, (self.width * 0.35, self.height * 0.12))
        self.screen.blit(label_surface, (self.width * 0.35, self.height * 0.10))

        spacing = 0.25
        start_x = self.width * 0.12
        start_y = self.height * spacing
        for highscore in self.highscores:
            text = f"-> {highscore["name"].upper()} : {highscore["score"]}"
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
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.commands_font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78

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

            if self.game_state == GameState.MENU:
                self.screen.blit(self.menu_background, (0, 0))
                # self.screen.fill("black")
                self._menu()

            elif self.game_state == GameState.PLAYING:
                self._play()

            elif self.game_state == GameState.HIGHSCORES:
                self.screen.blit(self.menu_background, (0, 0))
                self._highscores()
            
            elif self.game_state == GameState.INSTRUCTIONS:
                self.screen.blit(self.menu_background, (0, 0))
                self._instructions()

            elif self.game_state == GameState.EXIT:
                self.running = False

            elif self.game_state == GameState.PAUSED:
                self._paused()
                # for event in pygame.event.get():
                    # self._handle_paused_input()

            self.clock.tick(60)
            pygame.display.flip()
        

if __name__=="__main__":
    configs = load_config(sys.argv[-1])
    game = GameEngine(configs)
    game.run()
