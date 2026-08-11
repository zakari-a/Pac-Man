import pygame
import json
from enum import Enum
# from src.assets import assetmanager

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

class Menu():
    def __init__(self, assets, screen) -> None:
        # self.assets = assets
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.index = 0
        self.background = pygame.transform.scale(assets.background1, (self.width, self.height))
        self.font = assets.font_20
        self.menu_list = [
            ("START GAME", GameState.PLAYING),
            ("INSTRUCTIONS", GameState.INSTRUCTIONS),
            ("HIGHSCORES", GameState.HIGHSCORES),
            ("EXIT", GameState.EXIT)
            ]


    def run(self) -> None: 
        # self.lives = self.configs.lives
        spacing = 0.50
        start_x = self.width * 0.10
        start_y = self.height * spacing        
        for i, (label, state) in enumerate(self.menu_list):
            color = "white"
            if i == self.index:
                color = "yellow"
                label = f"→ {label}"
            label_surfacee = self.font.render(label, True, color)
            self.screen.blit(label_surfacee, (start_x, start_y))
            spacing += 0.07
            start_y = self.height * spacing


class Instructions():
    def __init__(self, assets, screen) -> None:
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.index = 0
        self.background = pygame.transform.scale(assets.background2, (self.width, self.height))
        self.font1 = assets.font_10
        self.font2 = assets.font_20
        self.font3 = assets.font_35
        self.sections = ["MOVEMENTS AND NAVIGATION :", "CHEATS :"]
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
        self.buttons = [("EXIT TO MAIN MENU", GameState.MENU), ("HIGHSCORES", GameState.HIGHSCORES)]


    def _draw_sections(self) -> None:
        start_x = self.width * 0.12
        start_y = self.height * 0.20
        for text in self.sections:
            label_surface = self.font2.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            start_x = self.width * 0.68

    def _draw_keys(self) -> None:
        coords = [
            (self.width * 0.15, self.height * 0.30),
            (self.width * 0.11, self.height * 0.36),
            (self.width * 0.15, self.height * 0.36),
            (self.width * 0.19, self.height * 0.36),
            (self.width * 0.15, self.height * 0.45),
            (self.width * 0.11, self.height * 0.51),
            (self.width * 0.15, self.height * 0.51),
            (self.width * 0.19, self.height * 0.51)
        ]
        keys = ["↑", "←", "↓", "→", "W", "A", "S", "D"]

        width = self.width * 0.03
        height = self.height * 0.05
        for i, coord in enumerate(coords):
            box_rect = pygame.Rect(coord[0], coord[1], width, height)
            pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
            label_surface = self.font1.render(keys[i], True, "white")
            label_rect = label_surface.get_rect(center=box_rect.center)
            self.screen.blit(label_surface, label_rect)
        
        box_rect = pygame.Rect(self.width * 0.125, self.height * 0.63, self.width * 0.08, self.height * 0.05)
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=3, border_radius=5)
        label_surface = self.font1.render("ESCAPE", True, "white")
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
            label_surface = self.font1.render(keys[i], True, "white")
            label_rect = label_surface.get_rect(center=box_rect.center)
            self.screen.blit(label_surface, label_rect)

    def _draw_inst_text(self) -> None:
        coords = [
            (self.width * 0.25, self.height * 0.36),
            (self.width * 0.25, self.height * 0.51),
            (self.width * 0.25, self.height * 0.65),
        ]

        for i, text in enumerate(self.movement_text):
            label_surface = self.font1.render(text, True, "white")
            self.screen.blit(label_surface, coords[i])
        
        spacing = 0.312
        start_x = self.width * 0.68
        start_y = self.height * spacing
        for text in self.cheats_text:
            label_surface = self.font1.render(text, True, "white")
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.067
            start_y = self.height * spacing

    def run(self) -> None:
        label_surface = self.font3.render("INSTRUCTION", True, "yellow")
        label_surface2 = self.font3.render("___________", True, "darkblue")
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (self.width * 0.02, self.height * 0.02))
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


        for i, (label, state) in enumerate(self.buttons):
            color = "darkblue"
            if i == self.index:
                color = "white"
                label = f"→ {label}"
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.font1.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78


class HighScores():
    def __init__(self, assets, screen, scores, file_name) -> None:
        self.screen = screen
        self.scores = scores
        self.file = file_name
        self.width, self.height = screen.get_size()
        self.index = 0
        self.background = pygame.transform.scale(assets.background2, (self.width, self.height))
        self.font1 = assets.font_10
        self.font2 = assets.font_20
        self.font3 = assets.font_35
        self.buttons = [("EXIT TO MAIN MENU", GameState.MENU), ("INSTRUCTIONS", GameState.INSTRUCTIONS)]
        self.name = ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]
        self.name_index = 0
        self.highscore = self.scores[0]["score"] if self.scores else 0


    def _update_highsocores(self, score) -> None:
        name = "".join(self.name).rstrip("_")
        self.scores.append({"name": name, "score": score})
        self.scores = sorted(self.scores, key=lambda value: value["score"], reverse=True)[:10]

        with open(self.file, "w") as f:
            json.dump(self.scores, f, indent=2)

    def enter_name(self, done, score) -> None:
        box_rect = pygame.Rect(self.width * 0.02, self.height * 0.02, 
                               self.width * 0.96, self.height * 0.8)
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (self.width * 0.02, self.height * 0.02))
        pygame.draw.rect(self.screen, "darkblue", box_rect, width=10, border_radius=50)
        message = "WELL DONE!" if done else "UNLUCKY"
        label_surface1 = self.font3.render(message, True, "white")
        label_surface2 = self.font1.render("ENTER YOUR NAME", True, "white")
        label_surface3 = self.font1.render("YOUR SCORE IS:", True, "white")
        label_surface4 = self.font3.render(f"{score}", True, "yellow")
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
            label_surface = self.font2.render(char, True, color)
            self.screen.blit(label_surface, (start_x, start_y))
            spacing += 0.025
            start_x = self.width * spacing

        x = self.width * 0.02
        y = self.height * 0.9
        box_width = self.width * 0.20
        box_height = self.height * 0.08
        text = "CONFIRM"
        color = "darkblue"
        if self.index == 1:
            color = "white"
            text = f"→ {text}"
        box_rect = pygame.Rect(x, y, box_width, box_height)
        pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
        label = self.font1.render(text, True, "white")
        label_rect = label.get_rect(center=box_rect.center)
        self.screen.blit(label, label_rect)

    def run(self) -> None:
        # self.screen.fill("black")
        label_surface = self.font3.render("HIGHSCORES", True, "yellow")
        label_surface2 = self.font3.render("__________", True, "darkblue")
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
        for i, highscore in enumerate(self.scores):
            text = f"→ {highscore["name"].upper()} : {highscore["score"]}"
            label_surface = self.font1.render(text, True, "white")
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
        for i, (label, state) in enumerate(self.buttons):
            color = "darkblue"
            if i == self.index:
                color = "white"
                label = f"→ {label}"
            box_rect = pygame.Rect(x, y,
                               box_width, box_height)
            pygame.draw.rect(self.screen, "black", box_rect, border_radius=50)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.font1.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)
            x = self.width * 0.78


class Paused():
    def __init__(self, assets, screen) -> None:
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.paused_list = [("RESUME", GameState.PLAYING) , ("EXIT TO MAIN MENU", GameState.MENU)]
        self.index = 0
        self.font = assets.font_20


    def run(self) -> None:
        # self.renderer._draw_maze()
        # self.renderer._draw_pacman(self.pacman)
        # self.renderer._draw_ghosts(self.ghosts, self.pacman, self.ghosts[0].position)
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
            if i == self.index:
                color = "white"
                label = f"→ {label}"
                
            pygame.draw.rect(self.screen, "black", box_rect)
            pygame.draw.rect(self.screen, color, box_rect, width=10, border_radius=50)
            label_surfacee = self.font.render(label, True, "white")
            label_rect = label_surfacee.get_rect(center=box_rect.center)
            self.screen.blit(label_surfacee, label_rect)