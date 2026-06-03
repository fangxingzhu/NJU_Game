import json
import math
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = ROOT / "assets" / "images" / "nju_handdrawn_original.jpg"
ANNOTATED_PATH = ROOT / "assets" / "images" / "nju_handdrawn_map.jpg"
MAP_PATH = ROOT / "data" / "map.json"
DEBUG_PATH = ROOT / "assets" / "images" / "nju_handdrawn_annotated_debug.png"
COLLISION_DEBUG_PATH = ROOT / "assets" / "images" / "nju_handdrawn_collision_debug.png"
REGIONS_PATH = ROOT / "data" / "annotated_handdrawn_regions.json"
COLLISION_MASK_PATH = ROOT / "assets" / "images" / "nju_handdrawn_collision_mask.png"


# Shrink collision regions inward so narrow visual gaps between buildings stay
# playable. Increase this odd filter size for more clearance.
COLLISION_SHRINK_FILTER = 49


MANUAL_CLEAR_PATHS = [
    # Leave a walkable lane between 学生创业园/南大记忆/南园20舍
    # and the 南园14舍、南园13舍 block below.
    [(620, 1150), (875, 1154), (875, 1183), (620, 1178)],
    # Leave a walkable lane between 赛珍珠楼/西南楼 and 声学楼.
    [(555, 848), (735, 842), (735, 885), (555, 895)],
]


INTERACTIVE_BUILDINGS = {
    "大礼堂",
    "北大楼",
}


def poly(points):
    return [[int(x), int(y)] for x, y in points]


MANUAL_REGIONS = [
    ("中美文化交流中心", "building", poly([(330, 180), (455, 170), (490, 210), (430, 245), (350, 230)])),
    ("科学楼", "building", poly([(455, 170), (530, 178), (535, 220), (486, 232), (470, 200)])),
    ("曾宪梓楼", "building", poly([(250, 200), (345, 190), (400, 248), (385, 350), (250, 330), (235, 270)])),
    ("安中楼", "building", poly([(390, 235), (505, 235), (520, 305), (475, 360), (390, 335)])),
    ("北门", "gate", poly([(555, 210), (625, 205), (630, 250), (560, 258)])),
    ("北边门", "gate", poly([(720, 250), (800, 245), (805, 288), (720, 295)])),
    ("化学楼", "building", poly([(590, 295), (710, 305), (725, 355), (690, 372), (585, 360)])),
    ("逸夫管理科学楼", "building", poly([(560, 350), (680, 350), (700, 410), (590, 420), (560, 392)])),
    ("费彝民楼", "building", poly([(735, 350), (825, 355), (825, 430), (745, 422)])),
    ("体育馆", "building", poly([(838, 400), (890, 410), (900, 455), (845, 462), (825, 430)])),
    ("吕志和游泳健身馆", "building", poly([(880, 445), (955, 430), (975, 515), (900, 525), (865, 490)])),
    ("足球场", "building", poly([(675, 440), (835, 455), (850, 690), (650, 690), (635, 500)])),
    ("苏富特大厦", "building", poly([(545, 405), (690, 430), (675, 690), (520, 675), (535, 500)])),
    ("田家炳楼", "building", poly([(525, 470), (650, 485), (650, 565), (530, 565)])),
    ("文科楼", "building", poly([(525, 565), (650, 565), (650, 650), (525, 650)])),
    ("唐仲英楼", "building", poly([(400, 400), (520, 415), (500, 660), (380, 645)])),
    ("西校门", "gate", poly([(580, 690), (660, 690), (665, 735), (575, 735)])),
    ("天文台", "building", poly([(300, 700), (475, 690), (520, 760), (390, 805), (290, 775)])),
    ("工程管理学院", "building", poly([(430, 785), (575, 785), (575, 825), (440, 825)])),
    ("赛珍珠楼", "building", poly([(585, 760), (660, 760), (655, 870), (580, 855)])),
    ("西南楼", "building", poly([(640, 765), (735, 760), (735, 835), (635, 830)])),
    ("声学楼", "building", poly([(585, 880), (680, 875), (690, 935), (570, 935)])),
    ("物理楼", "building", poly([(680, 920), (790, 910), (785, 1005), (670, 1000)])),
    ("知行楼", "building", poly([(675, 850), (750, 850), (748, 930), (668, 928)])),
    ("树华楼", "building", poly([(760, 850), (850, 850), (860, 900), (755, 905)])),
    ("小礼堂", "building", poly([(900, 855), (980, 850), (985, 900), (890, 905)])),
    ("戊己庚楼", "building", poly([(850, 505), (900, 510), (900, 620), (845, 615)])),
    ("甲乙楼", "building", poly([(900, 560), (970, 560), (970, 610), (900, 610)])),
    ("辛壬楼", "building", poly([(835, 680), (950, 695), (995, 780), (760, 770), (770, 710)])),
    ("北大楼", "building", poly([(980, 540), (1085, 545), (1090, 610), (980, 610)])),
    ("西大楼", "building", poly([(930, 610), (980, 615), (980, 690), (915, 680)])),
    ("东大楼", "building", poly([(1055, 640), (1130, 650), (1125, 710), (1045, 700)])),
    ("东北楼", "building", poly([(1085, 545), (1145, 555), (1145, 620), (1085, 615)])),
    ("东北门", "gate", poly([(1125, 510), (1195, 500), (1205, 552), (1135, 565)])),
    ("东大门", "gate", poly([(1125, 705), (1190, 700), (1200, 760), (1125, 770)])),
    ("大礼堂", "building", poly([(910, 690), (985, 695), (985, 755), (910, 755)])),
    ("教学楼", "building", poly([(770, 760), (990, 760), (1010, 820), (770, 815)])),
    ("地质实验楼", "building", poly([(1045, 730), (1140, 740), (1130, 810), (1035, 800)])),
    ("东南楼", "building", poly([(1040, 825), (1130, 835), (1120, 955), (1025, 950)])),
    ("校史博物馆", "building", poly([(900, 910), (1035, 920), (1030, 1010), (890, 1005)])),
    ("图书馆", "building", poly([(880, 930), (1020, 935), (1020, 1025), (880, 1015)])),
    ("科技馆", "building", poly([(1030, 900), (1115, 910), (1110, 1010), (1025, 1005)])),
    ("蒙民伟楼", "building", poly([(1010, 980), (1110, 985), (1110, 1055), (1005, 1050)])),
    ("正门", "gate", poly([(820, 1010), (875, 1005), (880, 1060), (820, 1065)])),
    ("学生创业园", "building", poly([(665, 1095), (730, 1105), (730, 1160), (650, 1150)])),
    ("南大记忆", "building", poly([(745, 1080), (845, 1080), (845, 1110), (745, 1110)])),
    ("南园20舍", "building", poly([(745, 1118), (845, 1118), (845, 1148), (745, 1148)])),
    ("南园14舍", "building", poly([(650, 1165), (770, 1160), (765, 1215), (650, 1215)])),
    ("南园13舍", "building", poly([(650, 1218), (760, 1220), (760, 1265), (645, 1265)])),
    ("南芳园餐厅", "building", poly([(775, 1210), (860, 1210), (860, 1260), (775, 1260)])),
    ("教育超市", "building", poly([(680, 1325), (750, 1315), (750, 1435), (680, 1435)])),
    ("食堂", "building", poly([(790, 1300), (870, 1300), (870, 1365), (790, 1365)])),
    ("南苑宾馆", "building", poly([(705, 1460), (790, 1460), (795, 1570), (690, 1560)])),
    ("广州路校门", "gate", poly([(840, 1530), (900, 1535), (905, 1600), (835, 1595)])),
    ("校医院", "building", poly([(1015, 1085), (1135, 1095), (1135, 1140), (1015, 1140)])),
    ("汉口路", "gate", poly([(880, 1065), (1020, 1065), (1020, 1115), (880, 1115)])),
    ("南园19舍", "building", poly([(910, 1125), (985, 1125), (985, 1165), (910, 1165)])),
    ("南园18舍", "building", poly([(910, 1165), (985, 1165), (985, 1200), (910, 1200)])),
    ("南园1舍", "building", poly([(995, 1195), (1060, 1195), (1060, 1228), (995, 1228)])),
    ("南园5舍", "building", poly([(1070, 1135), (1140, 1135), (1140, 1170), (1070, 1170)])),
    ("南园6舍", "building", poly([(1075, 1185), (1145, 1185), (1145, 1225), (1075, 1225)])),
    ("南园7舍", "building", poly([(1075, 1230), (1145, 1230), (1145, 1280), (1075, 1280)])),
    ("南园2舍", "building", poly([(930, 1210), (990, 1210), (990, 1250), (930, 1250)])),
    ("南园3舍", "building", poly([(930, 1260), (990, 1260), (990, 1300), (930, 1300)])),
    ("南园4舍", "building", poly([(890, 1285), (955, 1285), (955, 1330), (890, 1330)])),
    ("南园02栋", "building", poly([(900, 1340), (965, 1340), (965, 1395), (900, 1395)])),
    ("大学生活动中心", "building", poly([(960, 1340), (1060, 1340), (1065, 1400), (960, 1400)])),
    ("小粉桥校门", "gate", poly([(1090, 1300), (1185, 1305), (1185, 1370), (1090, 1370)])),
    ("陶园03栋", "building", poly([(900, 1395), (980, 1395), (985, 1450), (900, 1450)])),
    ("南园8舍", "building", poly([(900, 1495), (1000, 1495), (1000, 1535), (900, 1535)])),
    ("南园12舍", "building", poly([(1000, 1480), (1100, 1480), (1100, 1545), (1000, 1545)])),
    ("南园15舍", "building", poly([(1080, 1370), (1160, 1370), (1160, 1450), (1080, 1450)])),
    ("南园16舍", "building", poly([(1035, 1335), (1095, 1335), (1095, 1395), (1035, 1395)])),
    ("南园11舍", "building", poly([(1030, 1520), (1125, 1520), (1125, 1600), (1030, 1600)])),
]


LABELS_BY_POSITION = [name for name, _, _ in MANUAL_REGIONS]


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def bounds(polygon):
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]


def is_red(pixel):
    r, g, b = pixel
    return r > 165 and g < 125 and b < 120 and r > g * 1.35 and r > b * 1.35


def is_blue(pixel):
    r, g, b = pixel
    return b > 135 and g > 85 and r < 120 and b > r * 1.45


def fill_marked_regions(image, predicate, min_area):
    width, height = image.size
    pix = image.load()
    barrier_image = Image.new("L", image.size, 0)
    barrier = barrier_image.load()
    for y in range(height):
        for x in range(width):
            if predicate(pix[x, y]):
                barrier[x, y] = 255
    barrier_image = barrier_image.filter(ImageFilter.MaxFilter(7))
    barrier = barrier_image.load()

    outside = [[False] * width for _ in range(height)]
    queue = deque()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if outside[y][x] or barrier[x, y] > 0:
            continue
        outside[y][x] = True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height and not outside[ny][nx]:
                queue.append((nx, ny))

    interior = [[False] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            interior[y][x] = not outside[y][x] and barrier[x, y] == 0

    seen = [[False] * width for _ in range(height)]
    regions = []
    for sy in range(height):
        for sx in range(width):
            if seen[sy][sx] or not interior[sy][sx]:
                continue
            queue = deque([(sx, sy)])
            seen[sy][sx] = True
            points = []
            while queue:
                x, y = queue.popleft()
                points.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and interior[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
            if len(points) < min_area:
                continue
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            rect = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
            if rect[2] < 10 or rect[3] < 10:
                continue
            regions.append({"points": points, "rect": rect, "center": [rect[0] + rect[2] // 2, rect[1] + rect[3] // 2]})
    return regions


def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def component_polygon(points, max_points=16):
    point_set = set(points)
    boundary = []
    for x, y in points:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in point_set:
                boundary.append((x, y))
                break
    hull = convex_hull(boundary)
    if len(hull) <= max_points:
        return poly(hull)
    step = len(hull) / max_points
    return poly([hull[round(i * step) % len(hull)] for i in range(max_points)])


def polygon_center(polygon):
    return (
        round(sum(p[0] for p in polygon) / len(polygon)),
        round(sum(p[1] for p in polygon) / len(polygon)),
    )


def expanded_bounds(polygon, width, height, padding=28):
    x, y, w, h = bounds(polygon)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width - 1, x + w + padding)
    y2 = min(height - 1, y + h + padding)
    return x1, y1, x2, y2


def nearest_seed(seed, barrier, box):
    x1, y1, x2, y2 = box
    sx, sy = seed
    if x1 <= sx <= x2 and y1 <= sy <= y2 and barrier[sx, sy] == 0:
        return sx, sy
    for radius in range(1, 32):
        for y in range(max(y1, sy - radius), min(y2, sy + radius) + 1):
            for x in range(max(x1, sx - radius), min(x2, sx + radius) + 1):
                if barrier[x, y] == 0:
                    return x, y
    return None


def boundary_polygon_from_fill(points, max_points=26):
    point_set = set(points)
    boundary = []
    for x, y in points:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in point_set:
                boundary.append((x, y))
                break
    if len(boundary) < 3:
        return None

    cx = sum(x for x, _ in boundary) / len(boundary)
    cy = sum(y for _, y in boundary) / len(boundary)
    by_angle = {}
    for x, y in boundary:
        angle = round(math.atan2(y - cy, x - cx), 3)
        distance = (x - cx) ** 2 + (y - cy) ** 2
        if angle not in by_angle or distance > by_angle[angle][0]:
            by_angle[angle] = (distance, (x, y))
    ordered = [item[1] for _angle, item in sorted(by_angle.items())]
    if len(ordered) <= max_points:
        return poly(ordered)
    step = len(ordered) / max_points
    return poly([ordered[round(i * step) % len(ordered)] for i in range(max_points)])


def fill_region_from_drawn_line(image, kind, seed_polygon):
    width, height = image.size
    predicate = is_blue if kind == "gate" else is_red
    marker = Image.new("L", image.size, 0)
    marker_pixels = marker.load()
    source = image.load()
    x1, y1, x2, y2 = expanded_bounds(seed_polygon, width, height)
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if predicate(source[x, y]):
                marker_pixels[x, y] = 255

    # Thicken the user's line a little so small antialiasing gaps become closed.
    marker = marker.filter(ImageFilter.MaxFilter(7))
    barrier = marker.load()
    seed = nearest_seed(polygon_center(seed_polygon), barrier, (x1, y1, x2, y2))
    if seed is None:
        return seed_polygon

    queue = deque([seed])
    seen = set()
    points = []
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen:
            continue
        seen.add((x, y))
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            continue
        if barrier[x, y] > 0:
            continue
        points.append((x, y))
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen:
                queue.append((nx, ny))

    if len(points) < 40:
        return seed_polygon
    polygon = boundary_polygon_from_fill(points)
    return polygon or seed_polygon


def line_accurate_regions():
    annotated = Image.open(ANNOTATED_PATH).convert("RGB")
    regions = []
    for name, kind, seed_polygon in MANUAL_REGIONS:
        regions.append((name, kind, fill_region_from_drawn_line(annotated, kind, seed_polygon)))
    return regions


def detected_regions():
    return MANUAL_REGIONS


def build_collision_mask():
    image = Image.open(ANNOTATED_PATH).convert("RGB")
    width, height = image.size
    pix = image.load()
    marker = Image.new("L", image.size, 0)
    marker_pixels = marker.load()
    for y in range(height):
        for x in range(width):
            if is_red(pix[x, y]):
                marker_pixels[x, y] = 255
    marker = marker.filter(ImageFilter.MaxFilter(9))
    barrier = marker.load()

    outside = [[False] * width for _ in range(height)]
    queue = deque()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if outside[y][x] or barrier[x, y] > 0:
            continue
        outside[y][x] = True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height and not outside[ny][nx]:
                queue.append((nx, ny))

    mask = Image.new("L", image.size, 0)
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            if barrier[x, y] > 0 or not outside[y][x]:
                mask_pixels[x, y] = 255
    mask = mask.filter(ImageFilter.MinFilter(COLLISION_SHRINK_FILTER))
    clear_draw = ImageDraw.Draw(mask)
    for path in MANUAL_CLEAR_PATHS:
        clear_draw.polygon(path, fill=0)
    mask.save(COLLISION_MASK_PATH)
    return mask


def build_map(image_size):
    buildings = []
    collisions = []
    regions = detected_regions()
    for name, kind, polygon in regions:
        if kind != "gate" and name not in INTERACTIVE_BUILDINGS:
            continue
        walkable = kind == "gate"
        item = {
            "name": name,
            "rect": bounds(polygon),
            "polygon": polygon,
            "walkable": walkable,
            "inside_bg": "",
            "dialog": f"这里是{name}。",
        }
        buildings.append(item)
        if not walkable:
            collisions.append({"name": name, "rect": item["rect"], "polygon": polygon})
    return {
        "mode": "pixel",
        "background": "assets/images/nju_handdrawn_original.jpg",
        "collision_mask": "assets/images/nju_handdrawn_collision_mask.png",
        "image_size": list(image_size),
        "player_start": [850, 1280],
        "collisions": [],
        "buildings": buildings,
    }, regions


def save_debug(data, image, collision_mask):
    overlay = image.convert("RGBA")
    mask_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask_pixels = collision_mask.load()
    layer_pixels = mask_layer.load()
    for y in range(image.height):
        for x in range(image.width):
            if mask_pixels[x, y] > 0:
                layer_pixels[x, y] = (255, 35, 35, 62)
    overlay = Image.alpha_composite(overlay, mask_layer)
    draw = ImageDraw.Draw(overlay, "RGBA")
    font = load_font(13)
    small = load_font(9)
    for index, item in enumerate(data["buildings"], 1):
        polygon = [tuple(p) for p in item["polygon"]]
        color = (30, 150, 255, 35) if item["walkable"] else (255, 40, 40, 0)
        outline = (30, 150, 255, 230) if item["walkable"] else (255, 255, 255, 115)
        draw.polygon(polygon, fill=color)
        draw.line(polygon + [polygon[0]], fill=outline, width=2)
        x, y, w, h = item["rect"]
        label = f"{index}.{item['name']}"
        label_font = small if w < 78 or h < 35 else font
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx, ty = x + max(2, (w - tw) // 2), y + max(2, (h - th) // 2)
        draw.rectangle((tx - 3, ty - 2, tx + tw + 3, ty + th + 2), fill=(0, 0, 0, 160))
        draw.text((tx, ty - 2), label, fill=(255, 255, 255, 245), font=label_font)
    overlay.save(DEBUG_PATH)


def save_collision_debug(image, collision_mask):
    overlay = image.convert("RGBA")
    mask_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask_pixels = collision_mask.load()
    layer_pixels = mask_layer.load()
    for y in range(image.height):
        for x in range(image.width):
            if mask_pixels[x, y] > 0:
                layer_pixels[x, y] = (255, 20, 20, 82)
    Image.alpha_composite(overlay, mask_layer).save(COLLISION_DEBUG_PATH)


def main():
    image = Image.open(BACKGROUND_PATH).convert("RGB")
    use_existing_mask = "--from-existing-mask" in sys.argv
    if use_existing_mask:
        collision_mask = Image.open(COLLISION_MASK_PATH).convert("L")
    else:
        collision_mask = build_collision_mask()
    data, regions = build_map(image.size)
    MAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    REGIONS_PATH.write_text(json.dumps(regions, ensure_ascii=False, indent=2), encoding="utf-8")
    save_debug(data, image, collision_mask)
    save_collision_debug(image, collision_mask)
    print(f"regions: {len(regions)}, collisions: {len(data['collisions'])}")
    print(f"wrote {MAP_PATH}")
    action = "loaded" if use_existing_mask else "wrote"
    print(f"{action} {COLLISION_MASK_PATH}")
    print(f"wrote {REGIONS_PATH}")
    print(f"wrote {DEBUG_PATH}")
    print(f"wrote {COLLISION_DEBUG_PATH}")


if __name__ == "__main__":
    main()
