import pygame

from src.config import Scene
from src.start_screen import StartScreen
from src.save_select_scene import SaveSelectScene
from src.character_creation import CharacterCreationScene
from src.overworld import Overworld
from src.building_scene import BuildingScene
from src.save_manager import SaveManager
from src.game_menu import GameMenu
from src.time_system import TimeSystem
import src.config as cfg

class SceneManager:
    def __init__(self):
        self.current_scene = Scene.START
        self.player_data = None
        self.current_slot = None
        self.pending_new_slot = None
        self.save_manager = SaveManager()
        self.menu = GameMenu()
        self.menu_open = False
        self.time_system = TimeSystem()
        self.scenes = {
            Scene.START: StartScreen(),
            Scene.SAVE_SELECT: SaveSelectScene(self.save_manager),
            Scene.CHARACTER_CREATE: CharacterCreationScene(),
            Scene.OVERWORLD: Overworld(),
            Scene.BUILDING: BuildingScene()
        }
        self.pre_scene = None

    def switch_to(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = scene_name

    def update(self, events):
        if self.current_scene in (Scene.OVERWORLD, Scene.BUILDING) and not self.menu_open:
            self.time_system.update()
        if self.menu_open:
            return self.update_menu(events)

        if self.current_scene in (Scene.OVERWORLD, Scene.BUILDING):
            filtered_events = []
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.menu.open()
                    self.menu_open = True
                    # 不再将 ESC 事件传递给当前场景，避免冲突
                else:
                    filtered_events.append(event)
            events = filtered_events

        next_scene = self.scenes[self.current_scene].update(events)
        if not next_scene:
            return None

        if isinstance(next_scene, tuple):
            return self.handle_action(next_scene)

        self.handle_scene_change(next_scene)
        return None

    def update_menu(self, events):
        action = self.menu.update(events)
        if action == "continue":
            self.menu_open = False
        elif action == "save":
            self.menu_open = False
            self.pre_scene = self.current_scene
            self.scenes[Scene.SAVE_SELECT].set_mode("save", cfg.AUTO_SAVE_ENABLED)
            self.scenes[Scene.SAVE_SELECT].refresh()
            self.switch_to(Scene.SAVE_SELECT)
        elif action == "load":
            self.menu_open = False
            self.pre_scene = self.current_scene
            self.scenes[Scene.SAVE_SELECT].set_mode("load", cfg.AUTO_SAVE_ENABLED)
            self.scenes[Scene.SAVE_SELECT].refresh()
            self.switch_to(Scene.SAVE_SELECT)
        elif action == "exit":
            if cfg.AUTO_SAVE_ENABLED:
                self.save_current_game()
            return "quit"
        return None

    def handle_action(self, action):
        # 兼容不同长度的元组
        if len(action) == 2:
            name, slot = action
        else:
            name = action[0]
            slot = None

        if name == "new_save":
            self.pending_new_slot = slot
            self.scenes[Scene.CHARACTER_CREATE].reset()
            self.switch_to(Scene.CHARACTER_CREATE)
        elif name == "load_save":
            self.load_game(slot)
            self.menu_open = False  # 读档后关闭菜单，进入游戏
            # 不再停留在存档界面，无需返回键介入
        elif name == "save_game":
            self.current_slot = slot
            self.save_current_game()
            self.scenes[Scene.SAVE_SELECT].refresh()
        elif name == "back_to_menu":
            if self.pre_scene is not None:
                # 回到进入存档界面前的场景（大地图或建筑内部）
                self.switch_to(self.pre_scene)
                # 重新打开菜单
                self.menu.open()
                self.menu_open = True
                self.pre_scene = None
            else:
                # 从开始画面进入的读档界面 → 返回开始画面
                self.switch_to(Scene.START)
                self.menu_open = False
        return None

    def handle_scene_change(self, next_scene):
        if next_scene == Scene.SAVE_SELECT:
            self.scenes[Scene.SAVE_SELECT].refresh()

        if next_scene == Scene.OVERWORLD:
            if self.current_scene == Scene.CHARACTER_CREATE:
                self.player_data = self.scenes[Scene.CHARACTER_CREATE].created_player_data
                self.current_slot = self.pending_new_slot
                self.pending_new_slot = None
                # 重置时间系统到默认值（新游戏开始）
                self.time_system = TimeSystem()  # ← 新增这一行
                self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system)
                if cfg.AUTO_SAVE_ENABLED:
                    self.save_current_game()
            else:
                self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system)

        if next_scene == Scene.BUILDING and self.current_scene == Scene.OVERWORLD:
            nearby = self.scenes[Scene.OVERWORLD].nearby_building
            if nearby:
                is_night = self.time_system.is_night()
                self.scenes[Scene.BUILDING].enter(nearby, is_night, self.time_system)

        self.switch_to(next_scene)

    def save_current_game(self):
        if not self.current_slot or not self.player_data:
            return None
        current_building = None
        if self.current_scene == Scene.BUILDING:
            building_data = self.scenes[Scene.BUILDING].building_data
            current_building = building_data.get("name") if building_data else None

        # 获取当前时间状态
        ts = self.time_system
        game_time = {
            "day": ts.day,
            "hour": ts.hour,
            "minute": ts.minute
        }

        return self.save_manager.save(
            self.current_slot,
            self.player_data,
            self.current_scene,
            current_building,
            game_time=game_time
        )

    def load_game(self, slot):
        save_data = self.save_manager.load(slot)
        self.current_slot = slot
        self.player_data = self.save_manager.player_from_save(save_data)

        # 恢复游戏时间
        saved_time = save_data.get("game_time", {})
        self.time_system.day = saved_time.get("day", 1)
        self.time_system.hour = saved_time.get("hour", 8)
        self.time_system.minute = saved_time.get("minute", 0)

        # 初始化大地图玩家数据
        self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system)

        # 根据存档直接跳转到目标场景
        if save_data.get("scene") == Scene.BUILDING and save_data.get("current_building"):
            building = self.find_building(save_data.get("current_building"))
            if building:
                is_night = self.time_system.is_night()
                self.scenes[Scene.BUILDING].enter(building, is_night, self.time_system)
                self.switch_to(Scene.BUILDING)
                return

        # 默认进入大地图
        self.switch_to(Scene.OVERWORLD)

    def find_building(self, building_name):
        for building in self.scenes[Scene.OVERWORLD].map.buildings:
            if building.get("name") == building_name:
                return building
        return None

    def draw(self, screen):
        self.scenes[self.current_scene].draw(screen)
        if self.menu_open:
            self.menu.draw(screen, self.player_data, self.current_slot,self.time_system)
