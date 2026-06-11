import pygame
from src.config import TILE_SIZE


class BuildingManager:
    def __init__(self, game_map):
        self.buildings = game_map.buildings
        self.trigger_areas = []

        for building in self.buildings:
            rect_list = building.get('rects')
            if not rect_list:
                rect_list = [building['rect']] if 'rect' in building else []

            for rect_data in rect_list:
                bx, by, bw, bh = rect_data
                building_rect = pygame.Rect(
                    bx * TILE_SIZE, by * TILE_SIZE,
                    bw * TILE_SIZE, bh * TILE_SIZE
                )
                self.trigger_areas.append((building_rect.inflate(32, 32), building))

    def check_nearby(self, player_rect):
        for trigger_rect, building in self.trigger_areas:
            if trigger_rect.colliderect(player_rect):
                return building
        return None
