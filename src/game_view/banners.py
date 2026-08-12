import pygame
from typing import Any


class Banners():
    def __init__(self, assets: Any, screen: Any, renderer: Any) -> None:
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.assets = assets
        self.renderer = renderer
        self.counter = 0
        self.frame_tick = 0
        self.scale = 0.4
        self.shrink_x = 1
        self.shrink_y = 2
        self.target_width = self.width * self.shrink_x
        self.target_height = self.height / self.shrink_y

    def _move_frame(self):
        c_time = pygame.time.get_ticks()
        if c_time - self.frame_tick >= 1000:
            self.counter += 1
            self.frame_tick = pygame.time.get_ticks()

    def _victory(self, score) -> bool:
        self._move_frame()
        self.renderer._draw_maze()
        banner = self.assets.victory
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, (0, 0, 0, 170), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (0, 0))
        center_x, center_y = self.screen.get_rect().center
        if self.counter < 7:
            if self.shrink_x > 0.6 and self.shrink_y < 5.5:
                self.shrink_x -= 0.01
                self.shrink_y += 0.08
                self.target_width = self.width * self.shrink_x
                self.target_height = self.height / self.shrink_y

            banner = pygame.transform.smoothscale(
                banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(banner, banner_rect)
            if self.shrink_x <= 0.6:
                labels = [
                    ("YOUR CURRENT SCORE IS:", self.assets.font_20),
                    (f"{score}", self.assets.font_35),
                    ("NEXT LEVEL WILL START IN:", self.assets.font_20),
                    (f"{7 - self.counter}", self.assets.font_35)
                ]

                pos = [-75, -0, 75, 150]
                for i, (key, value) in enumerate(labels):
                    label = value.render(key, True, "white")
                    label_rect = label.get_rect(
                        center=(center_x, center_y + pos[i]))
                    self.screen.blit(label, label_rect)

        if self.counter == 7:
            banner = pygame.transform.smoothscale(
                banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)
            self.shrink_x = 1
            self.shrink_y = 2
            self.counter = 0
            return True

        return False

    def _game_over(self, done) -> bool:
        self._move_frame()
        banner = self.assets.game_over
        if done:
            banner = self.assets.finish
        self.renderer._draw_maze()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, (0, 0, 0, 170), overlay.get_rect(), border_radius=50)
        self.screen.blit(overlay, (0, 0))
        center_x, center_y = self.screen.get_rect().center
        if self.counter < 4:
            if self.shrink_x > 0.6 and self.shrink_y < 5.5:
                self.shrink_x -= 0.01
                self.shrink_y += 0.08
                self.target_width = self.width * self.shrink_x
                self.target_height = self.height / self.shrink_y

            banner = pygame.transform.smoothscale(
                banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)

        if self.counter == 4:
            banner = pygame.transform.smoothscale(
                banner, (self.target_width, self.target_height))
            banner_rect = banner.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(banner, banner_rect)
            self.shrink_x = 1
            self.shrink_y = 2
            self.counter = 0
            return True
        return False
