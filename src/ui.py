import pygame
from src.config import font2_path
import os

_font_cache = {}

def get_ui_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(font2_path, size)
    return _font_cache[size]

def draw_prompt(screen, text):
    if not text:
        return
    font = get_ui_font(24)
    text_surf = font.render(text, True, (255, 255, 255))
    padding = 20
    bg_width = text_surf.get_width() + padding * 2
    bg_height = text_surf.get_height() + padding
    bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
    bg_rect.centerx = screen.get_width() // 2
    bg_rect.top = 30

    # 半透明背景
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    screen.blit(bg_surface, bg_rect.topleft)

    text_x = bg_rect.x + padding
    text_y = bg_rect.y + padding // 2
    screen.blit(text_surf, (text_x, text_y))

def wrap_text(text, font, max_width):
    lines = []
    for raw_line in str(text).split("\n"):
        current = ""
        for char in raw_line:
            test_line = current + char
            if current and font.size(test_line)[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = test_line
        lines.append(current)
    return lines

def draw_dialog_box(screen, text):
    if not text:
        return
    font = get_ui_font(24)
    padding = 20
    box_width = screen.get_width() - 100
    max_text_width = box_width - padding * 2
    line_surfs = [
        font.render(line, True, (255, 255, 255))
        for line in wrap_text(text, font, max_text_width)
    ]
    line_gap = 6
    text_height = sum(surf.get_height() for surf in line_surfs) + line_gap * max(0, len(line_surfs) - 1)
    box_height = max(80, text_height + padding)
    box_x = 50
    box_y = screen.get_height() - box_height - 30

    # 半透明背景
    bg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 200))
    screen.blit(bg_surface, (box_x, box_y))

    # 白色边框
    pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

    # 文字（左对齐，垂直居中）
    text_x = box_x + padding
    text_y = box_y + (box_height - text_height) // 2
    for surf in line_surfs:
        screen.blit(surf, (text_x, text_y))
        text_y += surf.get_height() + line_gap

# 日月图标缓存
_sun_icon = None
_moon_icon = None

def _load_time_icons():
    global _sun_icon, _moon_icon
    if _sun_icon is None:
        sun_path = os.path.join("assets", "images", "sun_icon.png")
        moon_path = os.path.join("assets", "images", "moon_icon.png")
        if os.path.exists(sun_path):
            _sun_icon = pygame.image.load(sun_path).convert_alpha()
            _sun_icon = pygame.transform.scale(_sun_icon, (36, 36))
        if os.path.exists(moon_path):
            _moon_icon = pygame.image.load(moon_path).convert_alpha()
            _moon_icon = pygame.transform.scale(_moon_icon, (36, 36))

def draw_time_ui(screen, time_system):
    if not time_system:
        return
    _load_time_icons()

    # 获取时间信息
    time_str = time_system.get_time_string()          # "08:30"
    day_str = f"第{time_system.day}天"
    week_str = time_system.get_weekday()

    # 组合显示文本：时间 | 天数 | 星期
    display_text = f"{time_str}  {day_str}  {week_str}"

    if time_system.is_night():
        state_text = "夜晚"
        icon_surface = _moon_icon
    else:
        state_text = "白天"
        icon_surface = _sun_icon

    font = get_ui_font(20)
    text_surf = font.render(display_text, True, (255, 255, 255))

    # 布局参数
    padding = 10
    box_padding_y = 8
    icon_size = 36
    gap = 12

    box_width = text_surf.get_width() + icon_size + gap + 32
    box_height = max(icon_size, text_surf.get_height()) + box_padding_y * 2

    # 右上角定位
    box_x = screen.get_width() - box_width - padding
    box_y = padding

    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (24, 28, 42), box_rect)
    pygame.draw.rect(screen, (245, 230, 160), box_rect, 2)

    # 内框装饰
    inner_rect = box_rect.inflate(-6, -6)
    pygame.draw.rect(screen, (80, 88, 120), inner_rect, 1)

    # 图标
    if icon_surface:
        icon_x = box_x + 16
        icon_y = box_y + (box_height - icon_size) // 2
        screen.blit(icon_surface, (icon_x, icon_y))

    # 文字
    text_x = icon_x + icon_size + gap
    text_y = box_y + (box_height - text_surf.get_height()) // 2
    screen.blit(text_surf, (text_x, text_y))
