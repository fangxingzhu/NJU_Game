import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT / "assets" / "images" / "nju_handdrawn_original.jpg"
MAP_PATH = ROOT / "data" / "map.json"
DEBUG_PATH = ROOT / "assets" / "images" / "nju_handdrawn_pixel_debug.png"


# Coordinates are normalized to the hand-drawn image and converted to pixels at
# generation time. They are intentionally rectangles for the first calibration
# pass; the runtime also accepts polygons later.
FEATURES = [
    ("中美文化交流中心", (0.255, 0.075, 0.330, 0.135), False),
    ("科学楼", (0.350, 0.080, 0.410, 0.135), False),
    ("曾宪梓楼", (0.245, 0.130, 0.325, 0.205), False),
    ("安中楼", (0.335, 0.130, 0.405, 0.215), False),
    ("北门", (0.430, 0.120, 0.475, 0.165), True),
    ("北边门", (0.555, 0.125, 0.620, 0.165), True),
    ("化学楼", (0.480, 0.145, 0.555, 0.225), False),
    ("逸夫管理科学楼", (0.455, 0.195, 0.555, 0.270), False),
    ("黄辉民楼", (0.585, 0.165, 0.655, 0.230), False),
    ("体育馆", (0.640, 0.225, 0.720, 0.285), False),
    ("吕志和游泳健身馆", (0.705, 0.270, 0.775, 0.365), False),
    ("足球场", (0.525, 0.285, 0.665, 0.455), False),
    ("苏高科大楼", (0.410, 0.245, 0.455, 0.330), False),
    ("田家炳楼", (0.435, 0.285, 0.505, 0.350), False),
    ("交科楼", (0.435, 0.340, 0.510, 0.420), False),
    ("逸夫楼", (0.425, 0.410, 0.505, 0.470), False),
    ("唐仲英楼", (0.275, 0.275, 0.370, 0.375), False),
    ("西校门", (0.445, 0.470, 0.530, 0.505), True),
    ("天文台", (0.310, 0.470, 0.365, 0.530), False),
    ("工程管理学院", (0.360, 0.485, 0.455, 0.545), False),
    ("赛珍珠楼", (0.455, 0.540, 0.510, 0.595), False),
    ("西南楼", (0.505, 0.535, 0.580, 0.600), False),
    ("知行楼", (0.585, 0.610, 0.650, 0.665), False),
    ("树华楼", (0.635, 0.595, 0.690, 0.650), False),
    ("小礼堂", (0.705, 0.585, 0.765, 0.650), False),
    ("物理楼", (0.525, 0.665, 0.610, 0.735), False),
    ("声学楼", (0.455, 0.615, 0.530, 0.675), False),
    ("两厅楼", (0.710, 0.335, 0.760, 0.390), False),
    ("戊己庚楼", (0.660, 0.345, 0.705, 0.425), False),
    ("甲乙楼", (0.745, 0.390, 0.790, 0.440), False),
    ("辛壬楼", (0.670, 0.440, 0.720, 0.500), False),
    ("北大楼", (0.800, 0.345, 0.865, 0.410), False),
    ("西大楼", (0.745, 0.430, 0.795, 0.500), False),
    ("东大楼", (0.850, 0.420, 0.905, 0.490), False),
    ("东北楼", (0.875, 0.350, 0.925, 0.410), False),
    ("东北门", (0.875, 0.310, 0.965, 0.360), True),
    ("东大门", (0.890, 0.420, 0.960, 0.465), True),
    ("大礼堂", (0.730, 0.485, 0.805, 0.545), False),
    ("教学楼", (0.685, 0.515, 0.760, 0.570), False),
    ("东南楼", (0.855, 0.535, 0.925, 0.610), False),
    ("地质实验楼", (0.880, 0.475, 0.955, 0.535), False),
    ("校史博物馆", (0.735, 0.640, 0.835, 0.705), False),
    ("图书馆", (0.700, 0.665, 0.815, 0.760), False),
    ("科技馆", (0.875, 0.640, 0.940, 0.735), False),
    ("蒙民伟楼", (0.875, 0.735, 0.950, 0.790), False),
    ("正门", (0.650, 0.765, 0.730, 0.805), True),
    ("汉口路", (0.720, 0.765, 0.830, 0.800), True),
    ("学生创业园", (0.520, 0.805, 0.610, 0.845), False),
    ("南大记忆南园20舍", (0.615, 0.795, 0.725, 0.835), False),
    ("南园14舍", (0.540, 0.870, 0.635, 0.915), False),
    ("南园13舍", (0.540, 0.935, 0.635, 0.980), False),
    ("南芳园餐厅", (0.625, 0.925, 0.735, 0.995), False),
    ("教育超市", (0.515, 0.930, 0.605, 0.975), False),
    ("食堂", (0.620, 0.970, 0.740, 1.000), False),
    ("校医院", (0.830, 0.810, 0.955, 0.865), False),
    ("南园19舍", (0.735, 0.820, 0.810, 0.855), False),
    ("南园18舍", (0.750, 0.855, 0.825, 0.890), False),
    ("南园1舍", (0.785, 0.900, 0.860, 0.935), False),
    ("南园5舍", (0.870, 0.865, 0.945, 0.900), False),
    ("南园6舍", (0.875, 0.910, 0.950, 0.945), False),
    ("南园7舍", (0.880, 0.950, 0.955, 0.985), False),
    ("南园2舍", (0.750, 0.945, 0.825, 0.985), False),
    ("南园3舍", (0.750, 0.985, 0.825, 1.025), False),
    ("南园4舍", (0.720, 0.930, 0.800, 0.970), False),
    ("南园02栋", (0.730, 0.975, 0.805, 1.000), False),
    ("大学生活动中心", (0.790, 0.955, 0.900, 0.995), False),
    ("陶园03栋", (0.780, 0.990, 0.860, 1.000), False),
    ("南园01栋", (0.895, 0.955, 0.960, 0.995), False),
    ("南园16舍", (0.885, 0.990, 0.955, 1.000), False),
    ("南园15舍", (0.870, 0.965, 0.950, 1.000), False),
    ("南苑宾馆", (0.590, 0.970, 0.705, 1.000), False),
    ("南园8舍", (0.730, 0.965, 0.820, 1.000), False),
    ("南园11舍", (0.850, 0.970, 0.945, 1.000), False),
    ("南园12舍", (0.820, 0.945, 0.925, 0.985), False),
    ("小粉桥校门", (0.920, 0.965, 0.990, 1.000), True),
    ("广州路校门", (0.710, 0.965, 0.820, 1.000), True),
]


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def clamp_rect(rect, width, height):
    x1, y1, x2, y2 = rect
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return [round(x1), round(y1), round(x2 - x1), round(y2 - y1)]


def build_map():
    image = Image.open(IMAGE_PATH)
    width, height = image.size
    buildings = []
    collisions = []
    for name, box, walkable in FEATURES:
        x1, y1, x2, y2 = box
        rect = clamp_rect((x1 * width, y1 * height, x2 * width, y2 * height), width, height)
        item = {
            "name": name,
            "rect": rect,
            "walkable": walkable,
            "inside_bg": "",
            "dialog": f"这里是{name}。",
        }
        buildings.append(item)
        if not walkable:
            collisions.append({"name": name, "rect": rect})
    return {
        "mode": "pixel",
        "background": "assets/images/nju_handdrawn_original.jpg",
        "image_size": [width, height],
        "player_start": [round(width * 0.67), round(height * 0.78)],
        "collisions": collisions,
        "buildings": buildings,
    }


def save_debug(data):
    image = Image.open(IMAGE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    font = load_font(18)
    small = load_font(13)
    for b in data["buildings"]:
        x, y, w, h = b["rect"]
        color = (40, 150, 255, 80) if b.get("walkable") else (255, 40, 40, 80)
        outline = (20, 120, 255, 230) if b.get("walkable") else (255, 20, 20, 230)
        draw.rectangle((x, y, x + w, y + h), fill=color, outline=outline, width=3)
        f = small if len(b["name"]) > 5 else font
        bbox = draw.textbbox((0, 0), b["name"], font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx, ty = x + max(2, (w - tw) // 2), y + max(2, (h - th) // 2)
        draw.rectangle((tx - 3, ty - 3, tx + tw + 3, ty + th + 3), fill=(0, 0, 0, 155))
        draw.text((tx, ty - 2), b["name"], fill=(255, 255, 255, 245), font=f)
    image.save(DEBUG_PATH)


def main():
    data = build_map()
    MAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    save_debug(data)
    print(f"wrote {MAP_PATH}")
    print(f"wrote {DEBUG_PATH}")
    print(f"features: {len(data['buildings'])}")


if __name__ == "__main__":
    main()
