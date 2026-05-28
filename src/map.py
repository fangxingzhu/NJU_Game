import json
import pygame
from src.config import TILE_SIZE, MAP_COLS, MAP_ROWS, COLOR_BUILDING, COLOR_PATH


class GameMap:
    def __init__(self, map_file):
        with open(map_file, 'r', encoding='utf-8') as f: #打开地图的json文件，只读，utf-8编码
            data = json.load(f) #得到一个存储json文件的字典
        self.tiles = data['tiles']
        self.buildings = data['buildings']

    def get_tile(self, col, row):
        """获取指定行列的图块编号（0=道路，1=建筑），越界返回1"""
        if 0 <= col < MAP_COLS and 0 <= row < MAP_ROWS:
            return self.tiles[row][col]
        return 1  # 边界外视为障碍

    def is_walkable(self, col, row):
        return self.get_tile(col, row) != 1

    def draw(self, screen, camera_x, camera_y):
        """绘制整张地图"""
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                tile = self.tiles[row][col]
                x = col * TILE_SIZE - camera_x
                y = row * TILE_SIZE - camera_y
                if tile == 0:  # 道路
                    color = COLOR_PATH
                elif tile == 1:  # 建筑/墙壁
                    color = COLOR_BUILDING
                else:
                    color = (0, 0, 0)  # 未定义用黑色
                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))