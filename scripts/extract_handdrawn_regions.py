import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_handdrawn_pixel_map import FEATURES  # noqa: E402


IMAGE_PATH = ROOT / "assets" / "images" / "nju_handdrawn_original.jpg"
MAP_PATH = ROOT / "data" / "map.json"
DEBUG_PATH = ROOT / "assets" / "images" / "nju_handdrawn_polygon_debug.png"
REGION_PATH = ROOT / "data" / "handdrawn_polygon_regions.json"


# The hand-drawn image has a different usable-map origin than the earlier
# normalized anchors. Apply one final image-space registration so named regions
# sit on the actual buildings instead of drifting down-right.
GLOBAL_OFFSET = (-45, -24)


MANUAL_RECTS = {
    # The old anchors for the east edge and south dormitory area came from a
    # different flat-map proportion. These hand-tuned pixel rects keep the named
    # regions on the hand-drawn buildings instead of drifting into blank space.
    "甲乙楼": [990, 660, 46, 55],
    "大礼堂": [1035, 840, 48, 36],
    "地质实验楼": [1080, 805, 70, 54],
    "东南楼": [1052, 900, 70, 78],
    "科技馆": [1046, 1060, 72, 100],
    "蒙民伟楼": [1055, 1188, 78, 52],
    "校医院": [1070, 1320, 116, 58],
    "南园19舍": [965, 1328, 58, 24],
    "南园18舍": [965, 1386, 58, 24],
    "南园1舍": [1046, 1418, 52, 24],
    "南园5舍": [1110, 1372, 52, 24],
    "南园6舍": [1115, 1438, 52, 24],
    "南园7舍": [1120, 1488, 52, 24],
    "南园2舍": [976, 1452, 52, 24],
    "南园3舍": [976, 1510, 52, 24],
    "南园4舍": [916, 1486, 54, 22],
    "南园02栋": [940, 1410, 54, 22],
    "大学生活动中心": [1008, 1482, 70, 28],
    "陶园03栋": [946, 1540, 56, 20],
    "南园01栋": [1110, 1540, 50, 22],
    "南园16舍": [1108, 1590, 50, 20],
    "南园15舍": [1098, 1562, 52, 22],
    "南苑宾馆": [790, 1530, 74, 25],
    "南园8舍": [930, 1575, 58, 22],
    "南园11舍": [1055, 1610, 60, 22],
    "南园12舍": [1025, 1548, 62, 22],
    "教育超市": [760, 1482, 60, 24],
    "食堂": [828, 1450, 82, 34],
    "南芳园餐厅": [820, 1492, 92, 30],
    "广州路校门": [890, 1628, 110, 58],
    "小粉桥校门": [1125, 1618, 100, 60],
}


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def is_whiteish(r, g, b):
    return r > 205 and g > 205 and b > 195 and max(r, g, b) - min(r, g, b) < 70


def is_greenish(r, g, b):
    return g > r + 12 and g > b + 8 and g > 70


def is_dark_ink(r, g, b):
    return r < 64 and g < 72 and b < 64


def is_road_or_paper(r, g, b):
    return is_whiteish(r, g, b) or (r > 170 and g > 170 and b > 155 and max(r, g, b) - min(r, g, b) < 95)


def is_building_like(r, g, b):
    if is_road_or_paper(r, g, b) or is_greenish(r, g, b) or is_dark_ink(r, g, b):
        return False
    # Keep muted roof/wall colors, including gray, beige, blue, red and purple.
    if 55 <= r <= 225 and 45 <= g <= 215 and 45 <= b <= 220:
        if not (g > 145 and r < 130 and b < 130):
            return True
    return False


def clamp_rect(x1, y1, x2, y2, width, height):
    x1 = max(0, min(width - 1, round(x1)))
    y1 = max(0, min(height - 1, round(y1)))
    x2 = max(x1 + 1, min(width, round(x2)))
    y2 = max(y1 + 1, min(height, round(y2)))
    return [x1, y1, x2 - x1, y2 - y1]


def feature_rect(box, width, height):
    x1, y1, x2, y2 = box
    return clamp_rect(x1 * width, y1 * height, x2 * width, y2 * height, width, height)


def expand_rect(rect, amount, width, height):
    x, y, w, h = rect
    return clamp_rect(x - amount, y - amount, x + w + amount, y + h + amount, width, height)


def monotonic_hull(points):
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


def rect_to_polygon(rect):
    x, y, w, h = rect
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def apply_offset_to_rect(rect, width, height):
    x, y, w, h = rect
    dx, dy = GLOBAL_OFFSET
    return clamp_rect(x + dx, y + dy, x + dx + w, y + dy + h, width, height)


def apply_offset_to_polygon(polygon, width, height):
    dx, dy = GLOBAL_OFFSET
    shifted = []
    for x, y in polygon:
        shifted.append([max(0, min(width, x + dx)), max(0, min(height, y + dy))])
    return shifted


def shrink_rect(rect, factor=0.62):
    x, y, w, h = rect
    nw = max(8, round(w * factor))
    nh = max(8, round(h * factor))
    return [x + (w - nw) // 2, y + (h - nh) // 2, nw, nh]


def polygon_bounds(polygon):
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]


def sample_boundary_points(mask, origin_x, origin_y, stride=2):
    height = len(mask)
    width = len(mask[0]) if height else 0
    boundary = []
    for y in range(0, height, stride):
        for x in range(0, width, stride):
            if not mask[y][x]:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nx < 0 or ny < 0 or nx >= width or ny >= height or not mask[ny][nx]:
                    boundary.append((origin_x + x, origin_y + y))
                    break
    return boundary


def largest_components(mask, keep=1):
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    components = []

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
            if len(points) >= 20:
                components.append(points)

    components.sort(key=len, reverse=True)
    allowed = set()
    for comp in components[:keep]:
        allowed.update(comp)
    return [[(x, y) in allowed for x in range(width)] for y in range(height)]


def extract_polygon(image, rect, walkable):
    width, height = image.size
    if walkable:
        return rect_to_polygon(rect), rect, "walkable"

    search = expand_rect(rect, 6, width, height)
    x, y, w, h = search
    crop = image.crop((x, y, x + w, y + h)).filter(ImageFilter.MedianFilter(3))
    pixels = crop.load()
    mask = [[False] * w for _ in range(h)]

    for yy in range(h):
        for xx in range(w):
            mask[yy][xx] = is_building_like(*pixels[xx, yy])

    mask = largest_components(mask, keep=1)
    points = sample_boundary_points(mask, x, y, stride=2)

    if len(points) < 12:
        fallback = shrink_rect(rect)
        return rect_to_polygon(fallback), fallback, "fallback"

    hull = monotonic_hull(points)
    if len(hull) < 3:
        fallback = shrink_rect(rect)
        return rect_to_polygon(fallback), fallback, "fallback"

    polygon = [[int(px), int(py)] for px, py in hull]
    bounds = polygon_bounds(polygon)
    if bounds[2] < 8 or bounds[3] < 8:
        fallback = shrink_rect(rect)
        return rect_to_polygon(fallback), fallback, "fallback"
    return polygon, bounds, "segmented"


def build_map():
    image = Image.open(IMAGE_PATH).convert("RGB")
    width, height = image.size
    buildings = []
    collisions = []
    regions = []

    for name, box, walkable in FEATURES:
        rough_rect = feature_rect(box, width, height)
        if name in MANUAL_RECTS:
            rect = MANUAL_RECTS[name]
            polygon = rect_to_polygon(rect)
            source = "manual"
        else:
            polygon, rect, source = extract_polygon(image, rough_rect, walkable)
        rect = apply_offset_to_rect(rect, width, height)
        polygon = apply_offset_to_polygon(polygon, width, height)
        item = {
            "name": name,
            "rect": rect,
            "polygon": polygon,
            "walkable": walkable,
            "inside_bg": "",
            "dialog": f"这里是{name}。",
        }
        buildings.append(item)
        regions.append({"name": name, "source": source, "rect": rect, "polygon": polygon})
        if not walkable:
            collisions.append({"name": name, "rect": rect, "polygon": polygon})

    return {
        "mode": "pixel",
        "background": "assets/images/nju_handdrawn_original.jpg",
        "image_size": [width, height],
        "player_start": [round(width * 0.67), round(height * 0.78)],
        "collisions": collisions,
        "buildings": buildings,
    }, regions


def save_debug(data):
    image = Image.open(IMAGE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    font = load_font(15)
    small_font = load_font(10)

    for b in data["buildings"]:
        polygon = [tuple(point) for point in b.get("polygon", rect_to_polygon(b["rect"]))]
        if b.get("walkable"):
            fill = (40, 150, 255, 45)
            outline = (20, 120, 255, 230)
        else:
            fill = (255, 40, 40, 42)
            outline = (255, 20, 20, 230)
        draw.polygon(polygon, fill=fill)
        draw.line(polygon + [polygon[0]], fill=outline, width=3)

        x, y, w, h = b["rect"]
        label = b["name"]
        label_font = small_font if w < 72 or h < 32 else font
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = x + max(2, (w - tw) // 2)
        ty = y + max(2, (h - th) // 2)
        draw.rectangle((tx - 3, ty - 2, tx + tw + 3, ty + th + 2), fill=(0, 0, 0, 150))
        draw.text((tx, ty - 2), label, fill=(255, 255, 255, 245), font=label_font)

    DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(DEBUG_PATH)


def main():
    data, regions = build_map()
    MAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    REGION_PATH.write_text(json.dumps(regions, ensure_ascii=False, indent=2), encoding="utf-8")
    save_debug(data)
    segmented = sum(1 for r in regions if r["source"] == "segmented")
    fallback = sum(1 for r in regions if r["source"] == "fallback")
    print(f"wrote {MAP_PATH}")
    print(f"wrote {REGION_PATH}")
    print(f"wrote {DEBUG_PATH}")
    print(
        f"features: {len(data['buildings'])}, segmented: {segmented}, "
        f"fallback: {fallback}, collisions: {len(data['collisions'])}"
    )


if __name__ == "__main__":
    main()
