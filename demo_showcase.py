"""Automated two-minute showcase for the existing NJU campus game.

Run with:
    python demo_showcase.py

Controls:
    Space       Pause/resume
    Left/Right  Previous/next chapter
    R           Restart
    F11         Toggle fullscreen
    Esc         Quit
"""

import os
import subprocess
import sys

import pygame

from src.building_scene import BuildingScene
from src.character_creation import CharacterCreationScene
from src.config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, font1_path, font2_path
from src.game_menu import GameMenu
from src.map import GameMap
from src.minigame_crossroad import MinigameCrossroad
from src.music_manager import MusicManager
from src.overworld import Overworld
from src.player_data import PlayerData
from src.save_manager import SaveManager
from src.save_select_scene import SaveSelectScene
from src.start_screen import StartScreen
from src.time_system import TimeSystem


DEMO_DURATION = 126.0
HEADER_HEIGHT = 96
WINDOW_HEIGHT = SCREEN_HEIGHT + HEADER_HEIGHT


class Showcase:
    def __init__(self):
        self.start_screen = StartScreen()
        self.character_creation = CharacterCreationScene()
        self.overworld = Overworld()
        self.building_scene = BuildingScene()
        self.minigame = MinigameCrossroad()
        self.menu = GameMenu()

        # Keep showcase saves separate from normal game saves.
        self.save_manager = SaveManager(save_dir="demo_saves")
        self.save_scene = SaveSelectScene(self.save_manager)
        self.music = MusicManager(
            playlist=[
                "assets/sounds/blithemix.ogg",
                "assets/sounds/Alls Fair In Love.mp3",
                "assets/sounds/And Just Like That.mp3",
                "assets/sounds/Barroom Ballet.mp3",
                "assets/sounds/Funshine.mp3",
            ]
        )
        self.music.play()

        self.game_map = GameMap("data/map.json")
        self.buildings = {item["name"]: item for item in self.game_map.buildings}
        self.player = PlayerData("NJU", "男")
        self.player.dormitory = "南园1舍"
        self.time_system = TimeSystem(8, 0)

        self.title_font = pygame.font.Font(font1_path, 34)
        self.subtitle_font = pygame.font.Font(font2_path, 20)
        self.help_font = pygame.font.Font(font2_path, 16)

        self.elapsed = 0.0
        self.paused = False
        self.fullscreen = False
        self.last_shot = None
        self.entered_shot = False
        self.music_toggled = False
        self.demo_saved = False
        self.name_dialog_started = False
        self.name_dialog_process = None
        self.cursor_pos = None
        self.crossroad_fail_spawn_stage = 0

        self.shots = [
            (0.0, 8.0, "启 · 初入鼓楼", "动态开始画面 · 校园光影轮播", self.draw_start),
            (8.0, 18.0, "启 · 创建角色", "PowerShell 姓名输入 · 男女预览 · 南园1舍", self.draw_creation),
            (18.0, 29.0, "游 · 漫步校园", "真实移动速度 · 道路寻迹 · 摄像机跟随", self.draw_walk),
            (29.0, 35.0, "游 · 昼夜光影", "从白昼到夜色，建筑外景同步变化", self.draw_day_night),
            (35.0, 42.0, "探 · 图书馆", "进入建筑 · NPC 对话 · 选项分支", self.draw_library),
            (42.0, 49.0, "探 · 红色问答", "大礼堂校史题库 · 即时正误反馈", self.draw_quiz),
            (49.0, 57.0, "探 · 穿越车流：失败", "从入口开始 · 车流碰撞 · 生命值归零", self.draw_crossroad_fail),
            (57.0, 65.0, "探 · 穿越车流：成功", "重新进入 · 真实移动速度 · 胜利传送", self.draw_crossroad_win),
            (65.0, 74.0, "憩 · 宿舍休息", "南园1舍 · 夜晚入睡 · 次日清晨", self.draw_sleep),
            (74.0, 82.0, "憩 · 青春彩蛋", "第 29 行第 10 列 · 照片剧情 CG", self.draw_easter_egg),
            (82.0, 89.0, "夜 · 静谧时分", "23:00 后，普通建筑空无一人", self.draw_quiet_night),
            (89.0, 96.0, "夜 · 校门守望", "汉口路校门深夜仍有保安值守", self.draw_guard),
            (96.0, 104.0, "趣 · 当前状态", "姓名 · 性别 · 宿舍 · 位置 · 时间", self.draw_status),
            (104.0, 112.0, "趣 · 音乐控制", "左上角一键暂停与恢复校园歌单", self.draw_music),
            (112.0, 120.0, "趣 · 存档读档", "按钮悬浮 · 独立存档槽 · 自动存档开关", self.draw_save),
            (120.0, 126.0, "收 · 鼓楼余韵", "《鼓楼拾光》 · 南京大学鼓楼校区 RPG", self.draw_ending),
        ]

    def reset(self):
        self.elapsed = 0.0
        self.last_shot = None
        self.entered_shot = False
        self.music_toggled = False
        self.player = PlayerData("NJU", "男")
        self.player.dormitory = "南园1舍"
        self.time_system = TimeSystem(8, 0)
        self.name_dialog_started = False
        self.cursor_pos = None
        self.crossroad_fail_spawn_stage = 0

    def update(self, dt, events):
        self.music.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_RIGHT:
                    self.jump_shot(1)
                elif event.key == pygame.K_LEFT:
                    self.jump_shot(-1)
                elif event.key == pygame.K_r:
                    self.reset()

        if not self.paused:
            self.elapsed += dt
            if self.elapsed >= DEMO_DURATION:
                self.reset()

    def jump_shot(self, direction):
        index, _ = self.current_shot()
        target = max(0, min(len(self.shots) - 1, index + direction))
        self.elapsed = self.shots[target][0]
        self.last_shot = None
        if target == 1:
            self.name_dialog_started = False

    def current_shot(self):
        for index, shot in enumerate(self.shots):
            if shot[0] <= self.elapsed < shot[1]:
                return index, shot
        return len(self.shots) - 1, self.shots[-1]

    def draw(self, screen):
        index, shot = self.current_shot()
        self.entered_shot = index != self.last_shot
        if self.entered_shot:
            self.last_shot = index

        local_time = self.elapsed - shot[0]
        self.cursor_pos = None
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        original_get_pos = pygame.mouse.get_pos
        pygame.mouse.get_pos = lambda: self.cursor_pos or (-1000, -1000)
        try:
            shot[4](game_surface, local_time, shot[1] - shot[0])
        finally:
            pygame.mouse.get_pos = original_get_pos
        self.draw_demo_cursor(game_surface)

        if self.paused:
            self.draw_center_badge(game_surface, "演示已暂停")

        screen.fill((12, 16, 30))
        screen.blit(game_surface, (0, HEADER_HEIGHT))
        self.draw_chapter_overlay(screen, shot[2], shot[3], index)

    def draw_start(self, screen, local, duration):
        self.start_screen.update([])
        self.start_screen.draw(screen)

    def draw_creation(self, screen, local, duration):
        creation = self.character_creation
        if local >= 1.8 and not self.name_dialog_started:
            self.launch_name_dialog()
            self.name_dialog_started = True

        creation.name = "NJU" if local >= 4.3 else ""
        creation.dormitory_index = 0

        if local < 4.3:
            creation.gender = "男"
        elif local < 5.4:
            creation.gender = "男"
            self.set_demo_cursor((495, 356))
        elif local < 6.5:
            creation.gender = "女"
            self.set_demo_cursor((645, 356))
        elif local < 7.4:
            creation.gender = "男"
            self.set_demo_cursor((495, 356))
        elif local < 8.3:
            creation.gender = "男"
            self.set_demo_cursor((720, 445))
        else:
            creation.gender = "男"
            creation.dormitory_index = 1
            self.set_demo_cursor((540, 526))
        creation.draw(screen)

    def draw_walk(self, screen, local, duration):
        # Row 20 is entirely walkable. This 41-tile route runs at the same
        # 2 px/frame (120 px/s at 60 FPS) speed as normal keyboard movement.
        path = [(2, 20), (37, 20), (31, 20)]
        x, y, direction = self.position_on_path(path, local, 120.0)
        self.prepare_overworld(x, y, 10, int(local * 5), direction)
        self.overworld.player.moving = True
        self.overworld.draw(screen)

    def draw_day_night(self, screen, local, duration):
        hour = 16 + int(local * 1.15)
        if hour >= 24:
            hour -= 24
        self.prepare_overworld(19, 23, hour, 0, "down")
        self.overworld.draw(screen)

    def draw_library(self, screen, local, duration):
        scene = self.building_scene
        if self.entered_shot:
            self.time_system.hour = 15
            scene.enter(self.buildings["图书馆"], False, self.time_system, self.player)

        if local < 1.6:
            scene.mode = "intro"
        elif local < 3.2:
            case = self.buildings["图书馆"]["dialog_cases_day"][0]
            scene.current_dialog_case = case
            scene.mode = "npc_dialog_first"
            from src.dialog import DialogEngine
            scene.dialog_engine = DialogEngine([case["npc"]])
        elif local < 5.0:
            case = self.buildings["图书馆"]["dialog_cases_day"][0]
            scene.current_dialog_case = case
            scene.mode = "reply_choice"
            scene.dialog_engine = None
            self.set_demo_cursor((400, 278), local >= 4.4)
        elif local < 6.3:
            case = self.buildings["图书馆"]["dialog_cases_day"][0]
            scene.current_dialog_case = case
            scene.player_reply_text = case["options"][0]
            scene.mode = "player_reply"
            from src.dialog import DialogEngine
            scene.dialog_engine = DialogEngine([f"你：{scene.player_reply_text}"])
        else:
            case = self.buildings["图书馆"]["dialog_cases_day"][0]
            scene.mode = "npc_dialog_final"
            from src.dialog import DialogEngine
            scene.dialog_engine = DialogEngine([case["replies"][0]])
        scene.draw(screen)

    def draw_quiz(self, screen, local, duration):
        scene = self.building_scene
        if self.entered_shot:
            scene.enter(self.buildings["大礼堂"], False, self.time_system, self.player)
            scene.quiz_questions = self.buildings["大礼堂"]["quiz_questions"][:1]

        if local < 2.0:
            scene.mode = "quiz_intro"
            self.set_demo_cursor((400, 303), local >= 1.2)
        elif local < 5.0:
            scene.current_dialog_case = scene.quiz_questions[0]
            scene.mode = "quiz_question"
            scene.dialog_engine = None
            answer = scene.current_dialog_case.get("answer", 0)
            self.set_demo_cursor((400, 245 + answer * 54), local >= 4.2)
        else:
            scene.current_dialog_case = scene.quiz_questions[0]
            scene.quiz_feedback = scene.current_dialog_case["correct_reply"]
            scene.quiz_correct_count = 1
            scene.mode = "quiz_result"
        scene.draw(screen)

    def draw_crossroad_fail(self, screen, local, duration):
        game = self.minigame
        if self.entered_shot:
            game.enter(self.buildings["南园校门"], self.player)
            game.cars.clear()
            self.crossroad_fail_spawn_stage = 0

        spawn_times = (1.25, 2.95, 4.65)
        if game.game_state == "playing":
            game.player_direction = "up"
            game.player_moving = local < 1.3
            game.player_y = max(392, 512 - local * 96)
            game.player_frame_index = int(local * FPS / game.player_frame_delay) % 4

            if (
                self.crossroad_fail_spawn_stage < len(spawn_times)
                and local >= spawn_times[self.crossroad_fail_spawn_stage]
            ):
                index = self.crossroad_fail_spawn_stage
                game.cars.append(
                    {
                        "x": game.player_x + 290,
                        "y": game.player_y - 6,
                        "speed": 6.0,
                        "width": 145,
                        "height": 92,
                        "image": game.car_images[index % len(game.car_images)] if game.car_images else None,
                    }
                )
                self.crossroad_fail_spawn_stage += 1
            # Keep this demonstration deterministic while retaining the
            # minigame's real movement, collision, removal and invincibility.
            game.spawn_timer = 0
            game.update([])

        if game.show_result:
            self.set_demo_cursor((315, 372), local >= 7.2)
        game.draw(screen)

    def draw_crossroad_win(self, screen, local, duration):
        game = self.minigame
        if self.entered_shot:
            game.enter(self.buildings["南园校门"], self.player)

        if local < 1.0:
            game.player_y = 512
        elif local < 5.8:
            game.player_direction = "up"
            game.player_moving = True
            game.player_y = max(45, 512 - (local - 1.0) * 360)
            game.player_frame_index = int(local * FPS / game.player_frame_delay) % 4
            game.update([])
        else:
            game.player_y = 45
            game.game_state = "win"
            game.show_result = True
            game.cars.clear()
        if game.show_result:
            self.set_demo_cursor((400, 362), local >= 7.1)
        game.draw(screen)

    def draw_sleep(self, screen, local, duration):
        scene = self.building_scene
        if self.entered_shot:
            self.time_system.hour = 22
            self.time_system.minute = 30
            scene.enter(self.buildings["南园1舍"], True, self.time_system, self.player)

        if local < 2.0:
            scene.is_night = True
            scene.mode = "dialog"
        elif local < 5.0:
            scene.is_night = True
            scene.mode = "sleep_choice"
            scene.dialog_engine = None
            self.set_demo_cursor((400, 303), local >= 4.2)
        else:
            self.time_system.day = 2
            self.time_system.hour = 8
            self.time_system.minute = 0
            scene.is_night = False
            scene.mode = "sleep_result"
            from src.dialog import DialogEngine
            scene.dialog_engine = DialogEngine(["你睡了一觉，精神恢复。"])
        scene.draw(screen)

    def draw_easter_egg(self, screen, local, duration):
        self.prepare_overworld(10, 29, 17, 20, "down")
        self.overworld.easter_egg_active = True
        self.overworld.easter_egg_triggered = True
        self.overworld.easter_egg_step = 0 if local < 2.2 else 1 if local < 4.4 else 2
        if self.overworld.easter_egg_step == 2 and self.overworld.egg_cg_image is None:
            path = "assets/images/cg_southgate.png"
            if os.path.exists(path):
                self.overworld.egg_cg_image = pygame.image.load(path).convert()
        self.overworld.draw(screen)

    def draw_quiet_night(self, screen, local, duration):
        scene = self.building_scene
        if self.entered_shot:
            self.time_system.hour = 23
            self.time_system.minute = 15
            scene.enter(self.buildings["北大楼"], True, self.time_system, self.player)
        scene.draw(screen)

    def draw_guard(self, screen, local, duration):
        scene = self.building_scene
        if self.entered_shot:
            self.time_system.hour = 23
            scene.enter(self.buildings["汉口路校门"], True, self.time_system, self.player)

        cases = self.buildings["汉口路校门"]["dialog_cases_night"]
        case = cases[0]
        npc_text = case.get("npc", case.get("guard", "保安仍在值守。"))
        scene.current_dialog_case = case
        from src.dialog import DialogEngine
        if local < 2.0:
            scene.mode = "intro"
        elif local < 4.5:
            scene.mode = "npc_dialog_first"
            scene.dialog_engine = DialogEngine([npc_text])
        elif local < 6.0:
            scene.mode = "reply_choice"
            scene.dialog_engine = None
            self.set_demo_cursor((400, 278), local >= 5.2)
        else:
            scene.mode = "npc_dialog_final"
            scene.dialog_engine = DialogEngine([case["replies"][0]])
        scene.draw(screen)

    def draw_status(self, screen, local, duration):
        self.time_system.day = 2
        self.prepare_overworld(19, 20, 20, 24, "down")
        self.overworld.draw(screen)
        self.menu.mode = "status"
        self.menu.draw(screen, self.player, 1, self.time_system)

    def draw_music(self, screen, local, duration):
        self.prepare_overworld(19, 20, 20, 30, "right")
        self.set_demo_cursor((30, 30), 2.0 <= local < 2.5 or 5.0 <= local < 5.5)
        if 2.2 < local < 5.0:
            if not self.music_toggled:
                self.music.toggle()
                self.music_toggled = True
        elif self.music_toggled:
            self.music.toggle()
            self.music_toggled = False
        self.overworld.draw(screen)
        state = "音乐暂停" if not self.music.is_enabled() else "音乐播放中"
        self.draw_center_badge(screen, state)

    def draw_save(self, screen, local, duration):
        if not self.demo_saved:
            self.save_manager.save(
                1,
                self.player,
                "overworld",
                game_time={"day": 2, "hour": 20, "minute": 30},
            )
            self.demo_saved = True
        self.save_scene.set_mode("save" if local < duration / 2 else "load", True)
        self.save_scene.refresh()
        self.set_demo_cursor((380, 186), 1.0 <= local < 3.3 or 5.0 <= local < 7.3)
        self.save_scene.draw(screen)

    def draw_ending(self, screen, local, duration):
        if self.start_screen.bg_images:
            bg = self.start_screen.bg_images[0]
            screen.blit(pygame.transform.scale(bg, screen.get_size()), (0, 0))
        else:
            screen.fill((24, 28, 42))
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((10, 12, 24, min(205, 135 + int(local * 18))))
        screen.blit(shade, (0, 0))
        title = self.title_font.render("鼓楼拾光", True, (255, 226, 135))
        subtitle = self.subtitle_font.render("南京大学鼓楼校区 RPG", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 245))
        screen.blit(subtitle, (screen.get_width() // 2 - subtitle.get_width() // 2, 300))

    def prepare_overworld(self, tile_x, tile_y, hour, minute, direction):
        self.time_system.hour = hour
        self.time_system.minute = minute
        self.player.x = int(tile_x * TILE_SIZE)
        self.player.y = int(tile_y * TILE_SIZE)
        self.player.direction = direction
        self.overworld.enter(self.player, self.time_system, self.music)
        self.overworld.player.frame_index = int(self.elapsed * 8) % 4
        self.overworld.easter_egg_active = False
        self.overworld.easter_egg_step = 0
        self.overworld.egg_cg_image = None

    def position_on_path(self, points, elapsed, speed_pixels):
        remaining = max(0.0, elapsed * speed_pixels / TILE_SIZE)
        for index in range(len(points) - 1):
            x1, y1 = points[index]
            x2, y2 = points[index + 1]
            distance = abs(x2 - x1) + abs(y2 - y1)
            if remaining <= distance:
                amount = remaining / distance if distance else 0.0
                x = x1 + (x2 - x1) * amount
                y = y1 + (y2 - y1) * amount
                if x2 != x1:
                    direction = "right" if x2 > x1 else "left"
                else:
                    direction = "down" if y2 > y1 else "up"
                return x, y, direction
            remaining -= distance
        x1, y1 = points[-2]
        x2, y2 = points[-1]
        direction = "right" if x2 > x1 else "left" if x2 < x1 else "down" if y2 > y1 else "up"
        return x2, y2, direction

    def launch_name_dialog(self):
        if os.name != "nt" or os.environ.get("SDL_VIDEODRIVER") == "dummy":
            return
        command = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$form = New-Object System.Windows.Forms.Form
$form.Text = '输入姓名'
$form.Size = New-Object System.Drawing.Size(390,190)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $true
$label = New-Object System.Windows.Forms.Label
$label.Text = '请输入姓名：'
$label.Location = New-Object System.Drawing.Point(24,24)
$label.AutoSize = $true
$box = New-Object System.Windows.Forms.TextBox
$box.Location = New-Object System.Drawing.Point(24,55)
$box.Size = New-Object System.Drawing.Size(325,28)
$box.Font = New-Object System.Drawing.Font('Microsoft YaHei UI',12)
$button = New-Object System.Windows.Forms.Button
$button.Text = '确认'
$button.Location = New-Object System.Drawing.Point(260,100)
$button.Size = New-Object System.Drawing.Size(90,32)
$form.Controls.AddRange(@($label,$box,$button))
$button.Add_Click({ $form.Close() })
$form.Tag = 0
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 350
$timer.Add_Tick({
    $form.Tag = [int]$form.Tag + 1
    if ($form.Tag -eq 2) { $box.Text = 'N' }
    if ($form.Tag -eq 3) { $box.Text = 'NJ' }
    if ($form.Tag -eq 4) { $box.Text = 'NJU' }
    if ($form.Tag -ge 7) { $timer.Stop(); $form.Close() }
})
$form.Add_Shown({ $box.Focus(); $timer.Start() })
[void]$form.ShowDialog()
"""
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self.name_dialog_process = subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                creationflags=creationflags,
            )
        except OSError:
            self.name_dialog_process = None

    def set_demo_cursor(self, position, pressed=False):
        self.cursor_pos = (int(position[0]), int(position[1]))

    def draw_demo_cursor(self, screen):
        if self.cursor_pos is None:
            return
        x, y = self.cursor_pos
        points = [(x, y), (x + 3, y + 21), (x + 8, y + 15), (x + 14, y + 27), (x + 19, y + 24), (x + 13, y + 13), (x + 22, y + 12)]
        pygame.draw.polygon(screen, (255, 255, 255), points)
        pygame.draw.lines(screen, (24, 24, 30), True, points, 2)

    def draw_chapter_overlay(self, screen, title, subtitle, index):
        pygame.draw.rect(screen, (12, 16, 30), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

        title_surface = self.title_font.render(title, True, (255, 226, 135))
        subtitle_surface = self.subtitle_font.render(subtitle, True, (240, 240, 240))
        screen.blit(title_surface, (20, 8))
        screen.blit(subtitle_surface, (22, 49))

        progress = self.elapsed / DEMO_DURATION
        pygame.draw.rect(screen, (60, 65, 80), (0, HEADER_HEIGHT - 4, SCREEN_WIDTH, 4))
        pygame.draw.rect(screen, (255, 205, 90), (0, HEADER_HEIGHT - 4, int(SCREEN_WIDTH * progress), 4))

        counter = self.help_font.render(
            f"{index + 1:02d}/{len(self.shots):02d}  {int(self.elapsed):03d}s / {int(DEMO_DURATION)}s",
            True,
            (220, 220, 220),
        )
        screen.blit(counter, (SCREEN_WIDTH - counter.get_width() - 18, 16))

        help_text = "Space 暂停  ←/→ 跳段  R 重播  F11 全屏  Esc 退出"
        help_surface = self.help_font.render(help_text, True, (230, 230, 230))
        screen.blit(help_surface, (SCREEN_WIDTH - help_surface.get_width() - 18, 55))

    def draw_center_badge(self, screen, text):
        surface = self.subtitle_font.render(text, True, (255, 255, 255))
        rect = pygame.Rect(0, 0, surface.get_width() + 40, surface.get_height() + 24)
        rect.center = (screen.get_width() // 2, screen.get_height() // 2)
        bg = pygame.Surface(rect.size, pygame.SRCALPHA)
        bg.fill((24, 28, 42, 220))
        screen.blit(bg, rect)
        pygame.draw.rect(screen, (255, 205, 90), rect, 2)
        screen.blit(surface, (rect.centerx - surface.get_width() // 2, rect.centery - surface.get_height() // 2))


def create_window(fullscreen=False):
    flags = pygame.FULLSCREEN if fullscreen else 0
    return pygame.display.set_mode((SCREEN_WIDTH, WINDOW_HEIGHT), flags)


def main():
    pygame.init()
    pygame.display.set_caption("鼓楼拾光 · 自动演示")
    screen = create_window()
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    showcase = Showcase()

    while True:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                showcase.fullscreen = not showcase.fullscreen
                screen = create_window(showcase.fullscreen)

        showcase.update(dt, events)
        showcase.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
