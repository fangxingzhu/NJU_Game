import pygame

from src.config import Scene, TILE_SIZE
from src.start_screen import StartScreen
from src.save_select_scene import SaveSelectScene
from src.character_creation import CharacterCreationScene
from src.overworld import Overworld
from src.building_scene import BuildingScene
from src.save_manager import SaveManager
from src.game_menu import GameMenu
from src.time_system import TimeSystem
from src.music_manager import MusicManager

import src.config as cfg
from src.minigame_crossroad import MinigameCrossroad

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
            Scene.BUILDING: BuildingScene(),
            Scene.MINIGAME: MinigameCrossroad()
        }

        self.pre_scene = None
        # 用于记录进入小游戏前的玩家坐标
        self.minigame_origin_pos = None
        # 在 __init__ 中
        self.music_manager = MusicManager(playlist=[
            "assets/sounds/blithemix.ogg",
            "assets/sounds/Alls Fair In Love.mp3",  # 请替换为你的音乐文件
            "assets/sounds/And Just Like That.mp3",
            "assets/sounds/Barroom Ballet.mp3",
            "assets/sounds/Funshine.mp3",
        ])
        self.music_manager.play()

    def switch_to(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = scene_name

    def update(self, events):
        # 更新音乐切歌
        self.music_manager.update()
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
                else:
                    filtered_events.append(event)
            events = filtered_events

        # 小游戏场景独立处理
        if self.current_scene == Scene.MINIGAME:
            next_scene = self.scenes[Scene.MINIGAME].update(events)
            if isinstance(next_scene, tuple) and next_scene[0] == "exit_minigame":
                target_building = next_scene[1]
                # 只有胜利去汉口路校门才需要传送
                if target_building == "汉口路校门":
                    self.set_player_at_building(target_building)
                else:
                    # 回南园校门（失败/退出）：恢复为进入前的坐标
                    if self.minigame_origin_pos is not None:
                        self.player_data.x = self.minigame_origin_pos[0]
                        self.player_data.y = self.minigame_origin_pos[1]
                        # 让大地图场景应用这个位置
                        self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system, self.music_manager)
                    # 如果原点丢失，不做任何操作，当前玩家坐标已经是原来位置（但我们会记录，所以正常不会丢）
                self.minigame_origin_pos = None
                self.switch_to(Scene.OVERWORLD)
                return None
            elif next_scene is not None:
                self.handle_scene_change(next_scene)
            return None

        # 普通场景处理
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
            self.menu_open = False
        elif name == "save_game":
            self.current_slot = slot
            self.save_current_game()
            self.scenes[Scene.SAVE_SELECT].refresh()
        elif name == "back_to_menu":
            if self.pre_scene is not None:
                if self.pre_scene == Scene.OVERWORLD:
                    self.scenes[Scene.OVERWORLD].enter(
                        self.player_data, self.time_system, self.music_manager
                    )
                self.switch_to(self.pre_scene)
                self.menu.open()
                self.menu_open = True
                self.pre_scene = None
            else:
                self.switch_to(Scene.START)
                self.menu_open = False
        elif name == "start_minigame":
            building = slot
            # 记录进入小游戏前的玩家坐标
            if self.player_data:
                self.minigame_origin_pos = (self.player_data.x, self.player_data.y)
            self.scenes[Scene.MINIGAME].enter(
                building_data=building,
                player_data=self.player_data,
                return_building="南园校门"  # 默认值，实际由小游戏内部覆盖
            )
            self.switch_to(Scene.MINIGAME)
            return None
        return None

    def handle_scene_change(self, next_scene):
        if next_scene == Scene.SAVE_SELECT:
            self.scenes[Scene.SAVE_SELECT].refresh()

        if next_scene == Scene.OVERWORLD:
            if self.current_scene == Scene.CHARACTER_CREATE:
                self.player_data = self.scenes[Scene.CHARACTER_CREATE].created_player_data
                self.current_slot = self.pending_new_slot
                self.pending_new_slot = None
                self.time_system = TimeSystem()
                self.scenes[Scene.OVERWORLD].enter(
                    self.player_data, self.time_system, self.music_manager
                )
                if cfg.AUTO_SAVE_ENABLED:
                    self.save_current_game()
            else:
                self.scenes[Scene.OVERWORLD].enter(
                    self.player_data, self.time_system, self.music_manager
                )

        if next_scene == Scene.BUILDING and self.current_scene == Scene.OVERWORLD:
            nearby = self.scenes[Scene.OVERWORLD].nearby_building
            if nearby:
                is_night = self.time_system.is_night()
                self.scenes[Scene.BUILDING].enter(
                    nearby,
                    is_night,
                    self.time_system,
                    self.player_data
                )

        self.switch_to(next_scene)

    def save_current_game(self):
        if not self.current_slot or not self.player_data:
            return None
        current_building = None
        if self.current_scene == Scene.BUILDING:
            building_data = self.scenes[Scene.BUILDING].building_data
            current_building = building_data.get("name") if building_data else None

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

        saved_time = save_data.get("game_time", {})
        self.time_system.day = saved_time.get("day", 1)
        self.time_system.hour = saved_time.get("hour", 8)
        self.time_system.minute = saved_time.get("minute", 0)

        self.scenes[Scene.OVERWORLD].enter(
            self.player_data,
            self.time_system,
            self.music_manager
        )

        if save_data.get("scene") == Scene.BUILDING and save_data.get("current_building"):
            building = self.find_building(save_data.get("current_building"))
            if building:
                is_night = self.time_system.is_night()
                self.scenes[Scene.BUILDING].enter(building, is_night, self.time_system, self.player_data)
                self.switch_to(Scene.BUILDING)
                return

        self.switch_to(Scene.OVERWORLD)

    def find_building(self, building_name):
        for building in self.scenes[Scene.OVERWORLD].map.buildings:
            if building.get("name") == building_name:
                return building
        return None

    def set_player_at_building(self, building_name):
        if building_name == "汉口路校门":
            # 固定坐标：第19列，第19行
            self.player_data.x = 19 * TILE_SIZE
            self.player_data.y = 19 * TILE_SIZE
            self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system, self.music_manager)
            return

        # 其他建筑保留原有逻辑（如果需要）
        for building in self.scenes[Scene.OVERWORLD].map.buildings:
            if building.get("name") == building_name:
                rects = building.get("rects", [building.get("rect")] if building.get("rect") else [])
                if not rects:
                    break
                bottom_rect = max(rects, key=lambda r: r[1] + r[3])
                target_col = bottom_rect[0] + bottom_rect[2] // 2
                target_row = bottom_rect[1] + bottom_rect[3] + 1
                game_map = self.scenes[Scene.OVERWORLD].map
                while target_row < 30:
                    if game_map.is_walkable(target_col, target_row):
                        self.player_data.x = target_col * TILE_SIZE
                        self.player_data.y = target_row * TILE_SIZE
                        self.scenes[Scene.OVERWORLD].enter(self.player_data, self.time_system, self.music_manager)
                        return
                    target_row += 1
                break

    def draw(self, screen):
        self.scenes[self.current_scene].draw(screen)
        if self.menu_open:
            self.menu.draw(screen, self.player_data, self.current_slot, self.time_system)