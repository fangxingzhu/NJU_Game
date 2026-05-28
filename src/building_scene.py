import pygame
from src.config import Scene, font2_path

class BuildingScene:
    def __init__(self):
        self.building_data = None

    def enter(self, building_data):
        self.building_data = building_data

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.OVERWORLD
        return None

    def draw(self, screen):
        screen.fill((20, 20, 60))
        if self.building_data:
            font = pygame.font.Font(font2_path, 36)
            name_surf = font.render(f"进入 {self.building_data['name']}", True, (255,255,255))
            screen.blit(name_surf, (200, 250))
            tip_font = pygame.font.Font(font2_path, 24)
            tip_surf = tip_font.render("按 ESC 返回大地图", True, (200,200,200))
            screen.blit(tip_surf, (250, 350))