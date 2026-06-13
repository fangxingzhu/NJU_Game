import pygame
from src.config import Scene,TILE_SIZE,MAP_COLS,MAP_ROWS
from src.map import GameMap
from src.player import Player
from src.building import BuildingManager
from src.ui import draw_time_ui
from src.ui import draw_prompt, get_ui_font,draw_dialog_box
import os

class Overworld:
    def __init__(self):
        self.map = GameMap("data/map.json")
        # 玩家初始位置：道路区域，例如第24行20列
        self.player = Player(19*TILE_SIZE, 23*TILE_SIZE)
        self.player_data = None
        self.building_manager = BuildingManager(self.map)
        self.nearby_building = None
        self.time_system = None
        self.music_manager = None
        self.map_day = pygame.image.load("assets/images/overworld_daytime.png").convert()
        self.map_night = pygame.image.load("assets/images/overworld_nighttime.png").convert()
        # 彩蛋：地图上的照片事件
        self.easter_egg_triggered = False
        self.easter_egg_active = False
        self.easter_egg_step = 0
        self.egg_cg_image = None
        # 触发区域：第29行第10列，扩大一点方便触发
        egg_tile_x, egg_tile_y = 10, 29
        egg_pixel_x = egg_tile_x * TILE_SIZE
        egg_pixel_y = egg_tile_y * TILE_SIZE
        self.egg_trigger_rect = pygame.Rect(
            egg_pixel_x - TILE_SIZE, egg_pixel_y - TILE_SIZE,
            TILE_SIZE * 3, TILE_SIZE * 3
        )


    def enter(self, player_data=None, time_system=None, music_manager=None):
        self.player_data = player_data
        self.time_system = time_system
        self.music_manager = music_manager

        if player_data:
            self.player.x = player_data.x
            self.player.y = player_data.y
            self.player.direction = player_data.direction
            self.player.set_gender(player_data.gender)
            # 同步彩蛋触发状态（如果之前已找到，则不再触发）
            self.easter_egg_triggered = player_data.easter_egg_found

    def update(self, events):
        # 处理连续按键（移动）
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.player.speed
        if keys[pygame.K_RIGHT]:
            dx = self.player.speed
        if keys[pygame.K_UP]:
            dy = -self.player.speed
        if keys[pygame.K_DOWN]:
            dy = self.player.speed
        self.player.move(dx, dy, self.map)
        if self.player_data:
            self.player_data.x = self.player.x
            self.player_data.y = self.player.y
            self.player_data.direction = self.player.direction

        player_rect = pygame.Rect(self.player.x, self.player.y,
                                  self.player.width, self.player.height)
        self.nearby_building = self.building_manager.check_nearby(player_rect)
        # 彩蛋触发检测
        if not self.easter_egg_triggered and self.egg_trigger_rect.colliderect(player_rect):
            self.easter_egg_active = True
            self.easter_egg_triggered = True
            # 更新玩家数据中的标志，以便存档永久保存
            if self.player_data:
                self.player_data.easter_egg_found = True
            self.easter_egg_step = 0

        # 合并事件处理
        for event in events:
            # 彩蛋对话中的按键处理
            if self.easter_egg_active:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_e):
                    self.easter_egg_step += 1
                    if self.easter_egg_step == 2:
                        # 加载CG图片（按需，如果图片存在）
                        cg_path = "assets/images/cg_southgate.png"
                        if os.path.exists(cg_path):
                            self.egg_cg_image = pygame.image.load(cg_path).convert()
                        else:
                            self.egg_cg_image = None
                    elif self.easter_egg_step >= 3:
                        self.easter_egg_active = False
                        self.easter_egg_step = 0
                        self.egg_cg_image = None
                continue  # 彩蛋激活时忽略其他事件（移动、建筑交互等）
            # 鼠标点击音乐按钮
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                music_rect = pygame.Rect(10, 10, 40, 40)
                if music_rect.collidepoint(mouse_pos):
                    if self.music_manager:
                        self.music_manager.toggle()

            # 键盘按键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and self.nearby_building:
                    return Scene.BUILDING

        return None

    def draw(self, screen):
        # 摄像机计算（保持不变）
        camera_x = self.player.x - (screen.get_width() // 2) + (self.player.width // 2)
        camera_y = self.player.y - (screen.get_height() // 2) + (self.player.height // 2)
        max_camera_x = MAP_COLS * TILE_SIZE - screen.get_width()
        max_camera_y = MAP_ROWS * TILE_SIZE - screen.get_height()
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        # 绘制地图背景（替换原来的色块绘制）
        if self.time_system and self.time_system.is_night():
            screen.blit(self.map_night, (-camera_x, -camera_y))
        else:
            screen.blit(self.map_day, (-camera_x, -camera_y))

        # 绘制玩家、提示、时间等（保持不变）
        self.player.draw(screen, camera_x, camera_y)
        if self.nearby_building:
            prompt = f"按 E 进入{self.nearby_building['name']}"
        else:
            prompt = ""
        draw_prompt(screen, prompt)
        self.draw_menu_hint(screen)
        draw_time_ui(screen, self.time_system)
        self.draw_music_button(screen)

        # 彩蛋绘制
        if self.easter_egg_active:
            if self.easter_egg_step == 0:
                draw_dialog_box(screen, "这是什么？")
            elif self.easter_egg_step == 1:
                draw_dialog_box(screen, "一张照片？")
            elif self.easter_egg_step == 2 and self.egg_cg_image:
                # 全屏展示CG
                cg_scaled = pygame.transform.scale(self.egg_cg_image, (screen.get_width(), screen.get_height()))
                screen.blit(cg_scaled, (0, 0))
                draw_dialog_box(screen, "一张关于青春的珍贵照片……")  # 可以加一句描述

            # 在对话步骤0和1时，显示玩家立绘（类似建筑内部）
            if self.easter_egg_step in (0, 1) and self.player_data:
                gender = self.player_data.gender
                if gender == "女":
                    player_path = "assets/images/girl_portrait256.png"
                else:
                    player_path = "assets/images/boy_portrait256.png"
                if os.path.exists(player_path):
                    player_img = pygame.image.load(player_path).convert_alpha()
                    player_img = pygame.transform.scale(player_img, (160, 160))
                    screen.blit(player_img, (screen.get_width() - 220, screen.get_height() - 270))

            # 提示按键
            hint_font = get_ui_font(18)
            hint = hint_font.render("按空格继续", True, (200, 200, 200))
            screen.blit(hint, (screen.get_width() - hint.get_width() - 20, screen.get_height() - 30))


    def draw_menu_hint(self, screen):
        text_surf = get_ui_font(16).render("按 ESC 打开菜单", True, (60, 60, 60))
        padding = 10
        x = screen.get_width() - text_surf.get_width() - padding
        y = screen.get_height() - text_surf.get_height() - padding
        screen.blit(text_surf, (x, y))

    def draw_music_button(self, screen):
        if not self.music_manager:
            return
        font = get_ui_font(24)

        icon = "♪"
        if not self.music_manager.is_enabled():
            icon = "×"

        button_rect = pygame.Rect(
            10,
            10,
            40,
            40
        )

        pygame.draw.rect(
            screen,
            (88, 58, 120),
            button_rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (245,230,160),
            button_rect,
            2,
            border_radius=8
        )

        text = font.render(icon, True, (255,255,255))

        screen.blit(
            text,
            (
                button_rect.centerx - text.get_width()//2,
                button_rect.centery - text.get_height()//2
            )
        )

