import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT / "assets" / "images" / "nju_handdrawn_original.jpg"
MASK_PATH = ROOT / "assets" / "images" / "nju_handdrawn_walkable_mask.png"
DEBUG_PATH = ROOT / "assets" / "images" / "nju_handdrawn_precise_debug.png"
MAP_PATH = ROOT / "data" / "map.json"


BUILDINGS = [
    ("中美文化交流中心", [325, 160, 86, 50]),
    ("科学楼", [410, 150, 92, 58]),
    ("曾宪梓楼", [270, 190, 118, 138]),
    ("安中楼", [390, 190, 106, 100]),
    ("北门", [520, 176, 64, 74], True),
    ("北边门", [690, 186, 96, 68], True),
    ("化学楼", [585, 275, 58, 76]),
    ("逸夫管理科学楼", [550, 300, 82, 58]),
    ("黄辉民楼", [720, 350, 70, 45]),
    ("体育馆", [795, 386, 72, 58]),
    ("吕志和游泳健身馆", [902, 508, 82, 36]),
    ("足球场", [642, 450, 150, 218]),
    ("苏高科大楼", [516, 422, 46, 116]),
    ("田家炳楼", [523, 450, 82, 104]),
    ("交科楼", [523, 548, 82, 80]),
    ("逸夫楼", [510, 716, 26, 22]),
    ("唐仲英楼", [348, 522, 102, 92]),
    ("西校门", [540, 768, 116, 60], True),
    ("天文台", [358, 776, 84, 42]),
    ("工程管理学院", [450, 788, 78, 30]),
    ("赛珍珠楼", [570, 882, 62, 50]),
    ("西南楼", [655, 872, 76, 58]),
    ("知行楼", [725, 1068, 54, 36]),
    ("树华楼", [846, 980, 34, 32]),
    ("小礼堂", [880, 955, 90, 70]),
    ("物理楼", [640, 1105, 82, 36]),
    ("声学楼", [634, 1105, 28, 14]),
    ("两厅楼", [930, 560, 36, 32]),
    ("戊己庚楼", [872, 575, 28, 32]),
    ("甲乙楼", [948, 635, 48, 58]),
    ("辛壬楼", [832, 690, 78, 58]),
    ("北大楼", [1046, 568, 42, 32]),
    ("西大楼", [936, 740, 32, 30]),
    ("东大楼", [1065, 716, 38, 32]),
    ("东北楼", [1120, 582, 44, 60]),
    ("东北门", [1110, 500, 120, 84], True),
    ("东大门", [1126, 684, 94, 76], True),
    ("大礼堂", [990, 812, 54, 42]),
    ("教学楼", [858, 875, 42, 64]),
    ("东南楼", [1015, 874, 74, 78]),
    ("地质实验楼", [1035, 780, 76, 58]),
    ("校史博物馆", [950, 1070, 110, 94]),
    ("图书馆", [950, 1088, 94, 138]),
    ("科技馆", [1002, 1030, 80, 106]),
    ("蒙民伟楼", [1010, 1160, 84, 54]),
    ("正门", [810, 1265, 110, 64], True),
    ("汉口路", [900, 1262, 150, 58], True),
    ("学生创业园", [680, 1305, 48, 68]),
    ("南大记忆南园20舍", [760, 1285, 60, 24]),
    ("校医院", [1025, 1296, 116, 58]),
    ("南园19舍", [920, 1304, 58, 24]),
    ("南园18舍", [920, 1362, 58, 24]),
    ("南园1舍", [1001, 1394, 52, 24]),
    ("南园5舍", [1065, 1348, 52, 24]),
    ("南园6舍", [1070, 1414, 52, 24]),
    ("南园7舍", [1075, 1464, 52, 24]),
    ("南园2舍", [931, 1428, 52, 24]),
    ("南园3舍", [931, 1486, 52, 24]),
    ("南园4舍", [871, 1462, 54, 22]),
    ("南园02栋", [895, 1386, 54, 22]),
    ("大学生活动中心", [963, 1458, 70, 28]),
    ("陶园03栋", [901, 1516, 56, 20]),
    ("南园01栋", [1065, 1516, 50, 22]),
    ("南园16舍", [1063, 1566, 50, 20]),
    ("南园15舍", [1053, 1538, 52, 22]),
    ("南苑宾馆", [745, 1506, 74, 25]),
    ("南园8舍", [885, 1551, 58, 22]),
    ("南园11舍", [1010, 1586, 60, 22]),
    ("南园12舍", [980, 1524, 62, 22]),
    ("教育超市", [715, 1458, 60, 24]),
    ("食堂", [783, 1426, 82, 34]),
    ("南芳园餐厅", [775, 1468, 92, 30]),
    ("广州路校门", [845, 1604, 110, 58], True),
    ("小粉桥校门", [1080, 1594, 100, 60], True),
]


def is_road_white(r, g, b):
    return r > 202 and g > 198 and b > 188 and max(r, g, b) - min(r, g, b) < 58


def is_map_color(r, g, b):
    if r < 245 or g < 245 or b < 245:
        if not (r > 205 and g > 205 and b > 195 and max(r, g, b) - min(r, g, b) < 45):
            return True
    return False


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def rect_to_polygon(rect):
    x, y, w, h = rect
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def build_map_presence_image(image):
    width, height = image.size
    pix = image.load()
    presence = Image.new("L", (width, height), 0)
    out = presence.load()
    for y in range(height):
        for x in range(width):
            if is_map_color(*pix[x, y]):
                out[x, y] = 255
    return presence


def build_integral(mask_image):
    width, height = mask_image.size
    pix = mask_image.load()
    integral = [[0] * (width + 1) for _ in range(height + 1)]
    for y in range(height):
        row_sum = 0
        target = integral[y + 1]
        previous = integral[y]
        for x in range(width):
            row_sum += 1 if pix[x, y] > 0 else 0
            target[x + 1] = previous[x + 1] + row_sum
    return integral


def count_rect(integral, x1, y1, x2, y2):
    return integral[y2][x2] - integral[y1][x2] - integral[y2][x1] + integral[y1][x1]


def directional_presence(presence_image, radius):
    width, height = presence_image.size
    pix = presence_image.load()
    left = [[False] * width for _ in range(height)]
    right = [[False] * width for _ in range(height)]
    up = [[False] * width for _ in range(height)]
    down = [[False] * width for _ in range(height)]

    for y in range(height):
        distance = radius + 1
        for x in range(width):
            if pix[x, y] > 0:
                distance = 0
            else:
                distance += 1
            left[y][x] = 0 < distance <= radius

        distance = radius + 1
        for x in range(width - 1, -1, -1):
            if pix[x, y] > 0:
                distance = 0
            else:
                distance += 1
            right[y][x] = 0 < distance <= radius

    for x in range(width):
        distance = radius + 1
        for y in range(height):
            if pix[x, y] > 0:
                distance = 0
            else:
                distance += 1
            up[y][x] = 0 < distance <= radius

        distance = radius + 1
        for y in range(height - 1, -1, -1):
            if pix[x, y] > 0:
                distance = 0
            else:
                distance += 1
            down[y][x] = 0 < distance <= radius

    return left, right, up, down


def remove_small_components(mask, min_area):
    width, height = len(mask[0]), len(mask)
    seen = [[False] * width for _ in range(height)]
    out = [[False] * width for _ in range(height)]
    for sy in range(height):
        for sx in range(width):
            if seen[sy][sx] or not mask[sy][sx]:
                continue
            queue = deque([(sx, sy)])
            seen[sy][sx] = True
            points = []
            while queue:
                x, y = queue.popleft()
                points.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and mask[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
            if len(points) >= min_area:
                for x, y in points:
                    out[y][x] = True
    return out


def remove_border_components(mask):
    width, height = len(mask[0]), len(mask)
    seen = [[False] * width for _ in range(height)]
    out = [[False] * width for _ in range(height)]
    for sy in range(height):
        for sx in range(width):
            if seen[sy][sx] or not mask[sy][sx]:
                continue
            queue = deque([(sx, sy)])
            seen[sy][sx] = True
            points = []
            touches_outside = False
            while queue:
                x, y = queue.popleft()
                points.append((x, y))
                if x < 245 or y < 138 or x > 1248 or y > 1656 or (y < 330 and x > 650):
                    touches_outside = True
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and mask[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
            if not touches_outside:
                for x, y in points:
                    out[y][x] = True
    return out


def build_walkable_mask(image):
    image = image.convert("RGB").filter(ImageFilter.MedianFilter(3))
    width, height = image.size
    pix = image.load()
    presence = build_map_presence_image(image)
    integral = build_integral(presence)
    left, right, up, down = directional_presence(presence, 36)
    mask = [[False] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if y < 130 or x < 230 or x > 1260:
                continue
            if y < 330 and x > 650:
                continue
            if not is_road_white(*pix[x, y]):
                continue
            radius = 22
            x1, y1 = max(0, x - radius), max(0, y - radius)
            x2, y2 = min(width, x + radius + 1), min(height, y + radius + 1)
            local_map_pixels = count_rect(integral, x1, y1, x2, y2)
            side_count = sum((left[y][x], right[y][x], up[y][x], down[y][x]))
            enclosed = (left[y][x] and right[y][x]) or (up[y][x] and down[y][x]) or side_count >= 3
            if local_map_pixels >= 180 and enclosed:
                mask[y][x] = True

    mask = remove_small_components(mask, 120)
    mask = remove_border_components(mask)
    for entry in BUILDINGS:
        if len(entry) > 2 and entry[2]:
            x, y, w, h = entry[1]
            for yy in range(max(0, y), min(height, y + h)):
                for xx in range(max(0, x), min(width, x + w)):
                    mask[yy][xx] = True
    # Slightly erode the road mask so the player does not clip into building art.
    eroded = [[False] * width for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if mask[y][x] and all(mask[y + dy][x + dx] for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))):
                eroded[y][x] = True
    return eroded


def save_mask(mask):
    height = len(mask)
    width = len(mask[0])
    image = Image.new("L", (width, height), 0)
    pixels = image.load()
    for y, row in enumerate(mask):
        for x, value in enumerate(row):
            if value:
                pixels[x, y] = 255
    image.save(MASK_PATH)


def save_debug(image, mask, data):
    overlay = image.convert("RGBA")
    mask_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mp = mask_layer.load()
    for y, row in enumerate(mask):
        for x, value in enumerate(row):
            if value:
                mp[x, y] = (30, 180, 255, 72)
    overlay = Image.alpha_composite(overlay, mask_layer)
    draw = ImageDraw.Draw(overlay, "RGBA")
    font = load_font(15)
    small = load_font(10)

    for item in data["buildings"]:
        x, y, w, h = item["rect"]
        if item.get("walkable"):
            outline = (30, 120, 255, 230)
            fill = (30, 120, 255, 42)
        else:
            outline = (255, 35, 35, 220)
            fill = (255, 35, 35, 24)
        draw.rectangle((x, y, x + w, y + h), outline=outline, fill=fill, width=2)
        label_font = small if w < 72 or h < 32 else font
        bbox = draw.textbbox((0, 0), item["name"], font=label_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = x + max(2, (w - tw) // 2)
        ty = y + max(2, (h - th) // 2)
        draw.rectangle((tx - 3, ty - 2, tx + tw + 3, ty + th + 2), fill=(0, 0, 0, 150))
        draw.text((tx, ty - 2), item["name"], fill=(255, 255, 255, 245), font=label_font)
    overlay.save(DEBUG_PATH)


def build_json(image):
    width, height = image.size
    buildings = []
    for entry in BUILDINGS:
        name, rect = entry[0], entry[1]
        walkable = bool(entry[2]) if len(entry) > 2 else False
        buildings.append(
            {
                "name": name,
                "rect": rect,
                "polygon": rect_to_polygon(rect),
                "walkable": walkable,
                "inside_bg": "",
                "dialog": f"这里是{name}。",
            }
        )

    return {
        "mode": "pixel",
        "background": "assets/images/nju_handdrawn_original.jpg",
        "walkable_mask": "assets/images/nju_handdrawn_walkable_mask.png",
        "image_size": [width, height],
        "player_start": [880, 1288],
        "collisions": [],
        "buildings": buildings,
    }


def main():
    image = Image.open(IMAGE_PATH).convert("RGB")
    mask = build_walkable_mask(image)
    data = build_json(image)
    save_mask(mask)
    save_debug(image, mask, data)
    MAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    walkable_pixels = sum(sum(1 for value in row if value) for row in mask)
    print(f"wrote {MAP_PATH}")
    print(f"wrote {MASK_PATH}")
    print(f"wrote {DEBUG_PATH}")
    print(f"buildings: {len(data['buildings'])}, walkable_pixels: {walkable_pixels}")


if __name__ == "__main__":
    main()
