import pygame
from src.config import Scene
from src.start_screen import StartScreen
from src.overworld import Overworld
from src.building_scene import BuildingScene

class SceneManager:
    def __init__(self):
        self.current_scene = Scene.START
        self.scenes = {
            Scene.START: StartScreen(),
            Scene.OVERWORLD: Overworld(),
            Scene.BUILDING: BuildingScene()
        }

    def switch_to(self, scene_name):
        """切换到指定场景"""
        if scene_name in self.scenes:
            self.current_scene = scene_name

    def update(self, events):
        next_scene = self.scenes[self.current_scene].update(events)
        if next_scene:
            # 如果从大地图进入建筑，把建筑数据传给建筑场景
            if next_scene == Scene.BUILDING and self.current_scene == Scene.OVERWORLD:
                nearby = self.scenes[Scene.OVERWORLD].nearby_building
                if nearby:
                    self.scenes[Scene.BUILDING].enter(nearby)
            self.switch_to(next_scene)

    def draw(self, screen):
        """绘制当前场景"""
        self.scenes[self.current_scene].draw(screen)