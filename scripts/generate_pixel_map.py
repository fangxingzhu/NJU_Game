import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_FILE = ROOT / "data" / "map.json"
OUT_FILE = ROOT / "assets" / "images" / "campus_pixel_map.png"
TILE = 32

GRASS = (71, 126, 61)
GRASS_LIGHT = (91, 145, 73)
GRASS_DARK = (42, 91, 49)
PAVING = (168, 160, 132)
PAVING_DARK = (129, 122, 102)
ROAD = (63, 68, 70)
ROAD_EDGE = (183, 176, 154)
LANE = (214, 184, 83)
ROOF_BLUE = (48, 69, 91)
ROOF_GREEN = (53, 89, 72)
ROOF_GRAY = (95, 102, 109)
ROOF_RED = (132, 66, 52)
ROOF_BROWN = (138, 104, 77)
ROOF_ORANGE = (178, 102, 49)
WALL = (132, 88, 69)
WATER = (56, 132, 160)
WHITE = (238, 232, 210)
BLACK = (32, 29, 25)

BEIDA = "\u5317\u5927\u697c"
AUDITORIUM = "\u5927\u793c\u5802"
STADIUM = "\u8fd0\u52a8\u573a"
GATE = "\u95e8"
CANTEEN = "\u98df\u5802"
TEACHING = "\u6559\u5b66"
SCIENCE = "\u79d1\u5b66"
LIBRARY = "\u56fe\u4e66\u9986"
MONUMENT = "\u7eaa\u5ff5\u7891"
FOUNTAIN = "\u55b7\u6cc9"
LAWN = "\u5927\u7e9b\u576a"
MUSEUM = "\u6821\u53f2"
YIFU = "\u9038\u592b\u9986"
EAST = "\u4e1c\u5927\u697c"
WEST = "\u897f\u5927\u697c"
POOL = "\u6e38\u6cf3\u9986"


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT = load_font(15)
SMALL_FONT = load_font(12)


def rect_px(rect):
    x, y, w, h = rect
    return x * TILE, y * TILE, w * TILE, h * TILE


def save_map(data):
    lines = [
        "{",
        '  "background": "assets/images/campus_pixel_map.png",',
        '  "comment0": "以下地图数据来自 data/简化地图.xlsx；tiles 是二维数组，0=可通行区域，1=建筑/地标/场地，2=道路。",',
        '  "tiles": [',
    ]
    for index, row in enumerate(data["tiles"]):
        suffix = "," if index < len(data["tiles"]) - 1 else ""
        lines.append("    [" + ", ".join(str(value) for value in row) + "]" + suffix)
    lines.extend(
        [
            "  ],",
            '  "comment1": "以下建筑物数据来自 Excel 合并单元格；rect 为 [起始列, 起始行, 宽, 高]，使用零基地图坐标。",',
            '  "buildings": '
            + json.dumps(data["buildings"], ensure_ascii=False, indent=4).replace("\n", "\n  "),
            "}",
        ]
    )
    MAP_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_gates_walkable(data):
    for building in data["buildings"]:
        if GATE not in building["name"]:
            continue
        x, y, w, h = building["rect"]
        for row in range(y, y + h):
            for col in range(x, x + w):
                if 0 <= row < len(data["tiles"]) and 0 <= col < len(data["tiles"][0]):
                    data["tiles"][row][col] = 0


def draw_base(draw, width, height):
    draw.rectangle((0, 0, width, height), fill=GRASS)
    random.seed(44)
    for _ in range(8500):
        x = random.randrange(width)
        y = random.randrange(height)
        color = random.choice([GRASS, GRASS_LIGHT, GRASS_DARK, (61, 115, 58)])
        size = random.choice([1, 2, 2, 3])
        draw.rectangle((x, y, x + size, y + size), fill=color)
    for _ in range(120):
        x = random.randrange(width)
        y = random.randrange(height)
        r = random.randrange(10, 28)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=random.choice([(75, 132, 63), (82, 139, 67)]))


def draw_zebra(draw, x, y, vertical):
    for i in range(5):
        if vertical:
            draw.rectangle((x + i * 5, y, x + i * 5 + 2, y + 27), fill=(225, 225, 210))
        else:
            draw.rectangle((x, y + i * 5, x + 27, y + i * 5 + 2), fill=(225, 225, 210))


def draw_road_block(draw, x, y, w, h):
    draw.rectangle((x, y, x + w, y + h), fill=ROAD)
    draw.rectangle((x, y, x + w, y + 5), fill=ROAD_EDGE)
    draw.rectangle((x, y + h - 6, x + w, y + h), fill=ROAD_EDGE)
    draw.rectangle((x, y, x + 5, y + h), fill=ROAD_EDGE)
    draw.rectangle((x + w - 6, y, x + w, y + h), fill=ROAD_EDGE)
    if w >= h:
        mid = y + h // 2
        for lx in range(x + 14, x + w, 58):
            draw.rectangle((lx, mid - 2, lx + 20, mid + 2), fill=LANE)
        for sx in range(x + 20, x + w, 112):
            draw_zebra(draw, sx, y + 8, vertical=False)
    else:
        mid = x + w // 2
        for ly in range(y + 14, y + h, 58):
            draw.rectangle((mid - 2, ly, mid + 2, ly + 20), fill=LANE)
        for sy in range(y + 20, y + h, 112):
            draw_zebra(draw, x + 8, sy, vertical=True)


def draw_roads(draw, tiles):
    rows = len(tiles)
    cols = len(tiles[0])
    seen = set()
    for row in range(rows):
        for col in range(cols):
            if (col, row) in seen or tiles[row][col] != 2:
                continue
            w = 1
            while col + w < cols and tiles[row][col + w] == 2:
                w += 1
            h = 1
            while row + h < rows and all(tiles[row + h][col + i] == 2 for i in range(w)):
                h += 1
            for yy in range(row, row + h):
                for xx in range(col, col + w):
                    seen.add((xx, yy))
            draw_road_block(draw, col * TILE, row * TILE, w * TILE, h * TILE)


def draw_paving(draw, box, grid=True):
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=PAVING)
    if grid:
        for x in range(x1, x2, 16):
            draw.line((x, y1, x, y2), fill=(153, 145, 119))
        for y in range(y1, y2, 16):
            draw.line((x1, y, x2, y), fill=(153, 145, 119))
    draw.rectangle(box, outline=PAVING_DARK, width=1)


def draw_paths(draw, data):
    cx = 35 * TILE + TILE // 2
    draw_paving(draw, (cx - 13, 22 * TILE, cx + 13, 69 * TILE), grid=True)
    for y in (8, 14, 24, 37, 48, 60):
        draw_paving(draw, (4 * TILE, y * TILE - 10, 50 * TILE, y * TILE + 10), grid=True)
    for x in (7, 14, 21, 29, 41, 46):
        draw_paving(draw, (x * TILE - 9, 3 * TILE, x * TILE + 9, 49 * TILE), grid=True)
    for b in data["buildings"]:
        x, y, w, h = rect_px(b["rect"])
        if GATE in b["name"]:
            continue
        draw_paving(draw, (x - 6, y - 6, x + w + 6, y + h + 6), grid=True)


def label(draw, name, x, y, w, h):
    if w < 38 or h < 18:
        return
    text = name.replace("\u5b66\u751f", "")
    font = SMALL_FONT if len(text) > 5 or w < 92 else FONT
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    lx = x + (w - tw) // 2
    ly = y + (h - th) // 2
    draw.rectangle((lx - 4, ly - 4, lx + tw + 4, ly + th + 4), fill=(38, 30, 25), outline=(231, 218, 175))
    draw.text((lx, ly - 2), text, fill=WHITE, font=font)


def roof_shadow(draw, x, y, w, h):
    draw.rectangle((x + 5, y + 5, x + w + 5, y + h + 5), fill=(35, 70, 43))


def roof_rect(draw, box, fill, outline=BLACK):
    x1, y1, x2, y2 = box
    draw.rectangle((x1, y1, x2, y2), fill=fill, outline=outline)
    draw.rectangle((x1 + 4, y1 + 4, x2 - 4, y2 - 4), outline=tuple(max(0, c - 28) for c in fill), width=2)
    for y in range(y1 + 8, y2, 12):
        draw.line((x1 + 3, y, x2 - 3, y), fill=tuple(max(0, c - 18) for c in fill))


def roof_gable(draw, x, y, w, h, fill):
    roof_shadow(draw, x, y, w, h)
    draw.polygon((x, y + h // 2, x + w // 2, y, x + w, y + h // 2, x + w, y + h, x, y + h), fill=fill, outline=BLACK)
    draw.line((x + w // 2, y + 2, x + w // 2, y + h - 2), fill=tuple(max(0, c - 40) for c in fill), width=2)
    for yy in range(y + h // 2 + 6, y + h, 12):
        draw.line((x + 4, yy, x + w - 4, yy), fill=tuple(max(0, c - 25) for c in fill))


def roof_u_shape(draw, x, y, w, h, fill):
    roof_shadow(draw, x, y, w, h)
    bar = max(10, min(w, h) // 4)
    roof_rect(draw, (x, y, x + w, y + bar), fill)
    roof_rect(draw, (x, y, x + bar, y + h), fill)
    roof_rect(draw, (x + w - bar, y, x + w, y + h), fill)
    draw.rectangle((x + bar, y + bar, x + w - bar, y + h - 2), fill=(91, 143, 76), outline=(56, 101, 58))


def draw_windows_top(draw, x, y, w, h):
    color = (190, 215, 218)
    for wx in range(x + 8, x + w - 8, 18):
        draw.rectangle((wx, y + 5, wx + 5, y + 10), fill=color)
        draw.rectangle((wx, y + h - 11, wx + 5, y + h - 6), fill=color)
    for wy in range(y + 12, y + h - 12, 18):
        draw.rectangle((x + 5, wy, x + 10, wy + 5), fill=color)
        draw.rectangle((x + w - 11, wy, x + w - 6, wy + 5), fill=color)


def draw_building_roof(draw, building):
    name = building["name"]
    x, y, w, h = rect_px(building["rect"])
    inset = max(4, min(w, h) // 10)
    rx, ry = x + inset, y + inset
    rw, rh = max(10, w - inset * 2), max(10, h - inset * 2)

    if GATE in name:
        draw_gate(draw, name, (x, y, w, h))
        return
    if STADIUM in name:
        draw_stadium(draw, name, (x, y, w, h))
        return
    if FOUNTAIN in name or MONUMENT in name or LAWN in name:
        draw_landmark(draw, name, (x, y, w, h))
        return
    if POOL in name:
        draw_pool(draw, name, (x, y, w, h))
        return

    if name in {BEIDA, AUDITORIUM, EAST, WEST}:
        fill = ROOF_GREEN if name in {BEIDA, AUDITORIUM} else ROOF_BLUE
        roof_gable(draw, rx, ry, rw, rh, fill)
        if name == BEIDA:
            tower = max(14, min(rw, rh) // 3)
            roof_rect(draw, (rx + rw // 2 - tower // 2, ry + rh // 2 - tower // 2, rx + rw // 2 + tower // 2, ry + rh // 2 + tower // 2), ROOF_GREEN)
        draw_windows_top(draw, rx, ry, rw, rh)
    elif LIBRARY in name or YIFU in name or MUSEUM in name:
        roof_u_shape(draw, rx, ry, rw, rh, ROOF_RED)
        draw_windows_top(draw, rx, ry, rw, rh)
    elif CANTEEN in name:
        roof_rect(draw, (rx, ry, rx + rw, ry + rh), ROOF_ORANGE)
        draw.rectangle((rx + 6, ry + rh - 11, rx + rw - 6, ry + rh - 4), fill=(230, 210, 150), outline=BLACK)
    elif TEACHING in name or SCIENCE in name:
        roof_rect(draw, (rx, ry, rx + rw, ry + rh), ROOF_GRAY)
        skylight_count = max(1, rw // 70)
        for i in range(skylight_count):
            sx = rx + 12 + i * 48
            draw.rectangle((sx, ry + rh // 2 - 5, sx + 18, ry + rh // 2 + 5), fill=(160, 196, 206), outline=BLACK)
    else:
        roof_rect(draw, (rx, ry, rx + rw, ry + rh), ROOF_BROWN)
        draw_windows_top(draw, rx, ry, rw, rh)

    label(draw, name, x, y, w, h)


def draw_stadium(draw, name, box):
    x, y, w, h = box
    draw.rounded_rectangle((x + 8, y + 8, x + w - 8, y + h - 8), radius=min(w, h) // 4, fill=(179, 91, 58), outline=WHITE, width=3)
    draw.rounded_rectangle((x + 22, y + 22, x + w - 22, y + h - 22), radius=max(8, min(w, h) // 5), fill=(49, 132, 61), outline=WHITE, width=2)
    fx1, fy1, fx2, fy2 = x + w // 2 - 78, y + h // 2 - 45, x + w // 2 + 78, y + h // 2 + 45
    draw.rectangle((fx1, fy1, fx2, fy2), outline=(215, 236, 208), width=2)
    draw.line((fx1, y + h // 2, fx2, y + h // 2), fill=(215, 236, 208))
    draw.ellipse((x + w // 2 - 18, y + h // 2 - 18, x + w // 2 + 18, y + h // 2 + 18), outline=(215, 236, 208))
    label(draw, name, x, y, w, h)


def draw_pool(draw, name, box):
    x, y, w, h = box
    roof_rect(draw, (x + 7, y + 7, x + w - 7, y + h - 7), ROOF_GRAY)
    draw.rectangle((x + 16, y + 16, x + w - 16, y + h - 16), fill=WATER, outline=WHITE, width=2)
    for yy in range(y + 24, y + h - 16, 12):
        draw.line((x + 18, yy, x + w - 18, yy), fill=(130, 205, 220))
    label(draw, name, x, y, w, h)


def draw_landmark(draw, name, box):
    x, y, w, h = box
    cx, cy = x + w // 2, y + h // 2
    if FOUNTAIN in name:
        draw.ellipse((x + 6, y + 6, x + w - 6, y + h - 6), fill=WATER, outline=WHITE, width=2)
        for r in range(7, min(w, h) // 2, 8):
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(146, 215, 224))
    elif MONUMENT in name:
        draw_paving(draw, (x + 4, y + 4, x + w - 4, y + h - 4))
        draw.polygon((cx, y + 6, cx + 8, cy, cx, y + h - 6, cx - 8, cy), fill=(205, 196, 170), outline=BLACK)
    else:
        draw_paving(draw, (x + 4, y + 4, x + w - 4, y + h - 4))
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=GRASS_LIGHT, outline=WHITE)
    label(draw, name, x, y, w, h)


def draw_gate(draw, name, box):
    x, y, w, h = box
    draw_paving(draw, (x, y, x + w, y + h))
    for gx in (x + w // 4, x + w * 3 // 4):
        draw.rectangle((gx - 5, y + 4, gx + 5, y + h - 4), fill=WALL, outline=BLACK)
        draw.rectangle((gx - 8, y + 1, gx + 8, y + 7), fill=ROOF_GREEN, outline=BLACK)
    draw.rectangle((x + 6, y + h // 2 - 3, x + w - 6, y + h // 2 + 3), fill=(112, 75, 56), outline=BLACK)
    label(draw, name, x, y, w, h)


def draw_extra_roofs(draw, data):
    occupied = set()
    for b in data["buildings"]:
        x, y, w, h = b["rect"]
        for row in range(max(0, y - 1), min(len(data["tiles"]), y + h + 1)):
            for col in range(max(0, x - 1), min(len(data["tiles"][0]), x + w + 1)):
                occupied.add((col, row))
    extras = [(6, 19, 3, 3), (4, 34, 3, 3), (12, 31, 3, 2), (3, 53, 4, 2), (48, 8, 3, 3), (48, 52, 3, 3), (24, 55, 3, 3), (13, 58, 4, 2)]
    for rect in extras:
        x, y, w, h = rect
        if any((col, row) in occupied for row in range(y, y + h) for col in range(x, x + w)):
            continue
        draw_building_roof(draw, {"name": "", "rect": rect})


def draw_tree(draw, x, y, r):
    shadow = (37, 77, 43)
    draw.ellipse((x - r + 4, y - r + 5, x + r + 4, y + r + 5), fill=shadow)
    colors = [(38, 96, 49), (47, 112, 54), (66, 133, 61), (83, 151, 69)]
    for dx, dy, rr in [(-4, 1, r), (4, -2, r - 1), (0, 5, r - 2)]:
        draw.ellipse((x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr), fill=random.choice(colors), outline=(31, 73, 38))


def draw_trees(draw, data):
    occupied = set()
    for b in data["buildings"]:
        x, y, w, h = b["rect"]
        for row in range(max(0, y - 1), min(len(data["tiles"]), y + h + 1)):
            for col in range(max(0, x - 1), min(len(data["tiles"][0]), x + w + 1)):
                occupied.add((col, row))
    random.seed(925)
    for row, values in enumerate(data["tiles"]):
        for col, tile in enumerate(values):
            if tile == 2 or (col, row) in occupied:
                continue
            chance = 0.2 if tile == 0 else 0.34
            if random.random() < chance:
                draw_tree(draw, col * TILE + random.randint(6, 24), row * TILE + random.randint(6, 24), random.randint(6, 10))


def main():
    data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    make_gates_walkable(data)
    save_map(data)

    tiles = data["tiles"]
    width = len(tiles[0]) * TILE
    height = len(tiles) * TILE
    image = Image.new("RGB", (width, height), GRASS)
    draw = ImageDraw.Draw(image)

    draw_base(draw, width, height)
    draw_roads(draw, tiles)
    draw_paths(draw, data)
    draw_extra_roofs(draw, data)
    draw_trees(draw, data)
    for building in data["buildings"]:
        draw_building_roof(draw, building)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT_FILE)
    print(f"generated {OUT_FILE} ({width}x{height})")


if __name__ == "__main__":
    main()
