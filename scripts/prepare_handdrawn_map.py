import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"
MAP_FILE = ROOT / "data" / "map.json"
OUT_BG = IMAGE_DIR / "nju_handdrawn_map.png"
OUT_DEBUG = IMAGE_DIR / "nju_handdrawn_debug_overlay.png"
TILE = 32


def find_source():
    for name in (
        "nju_handdrawn_original.jpg",
        "nju_handdrawn_original.jpeg",
        "nju_handdrawn_original.png",
        "nju_handdrawn_original.webp",
    ):
        path = IMAGE_DIR / name
        if path.exists():
            return path
    raise FileNotFoundError(
        "Please save the hand-drawn map as assets/images/nju_handdrawn_original.jpg "
        "or .png/.webp first."
    )


def load_font(size):
    for path in (
        ROOT / "assets" / "fonts" / "NotoSansSC-VariableFont_wght.ttf",
        ROOT / "assets" / "fonts" / "NotoSerifSC-VariableFont_wght.ttf",
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def auto_crop_box(image):
    # Keep the main campus drawing and discard the decorative title, border,
    # article block, sketch inset, and seal/logo areas. The source image is a
    # poster, so this crop intentionally favors the right-side map body.
    w, h = image.size
    return (
        int(w * 0.24),
        int(h * 0.07),
        int(w * 0.93),
        int(h * 0.96),
    )


def set_background_path():
    data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    data["background"] = "assets/images/nju_handdrawn_map.png"
    MAP_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def clean_non_map_content(background):
    draw = ImageDraw.Draw(background)
    w, h = background.size
    cleanup_boxes = [
        # Large title/signature area in the upper-right.
        (int(w * 0.55), 0, w, int(h * 0.17)),
        # Poster stamp near the lower-left of the north campus map.
        (int(w * 0.15), int(h * 0.48), int(w * 0.37), int(h * 0.62)),
        # Long article block and sketch inset in the lower-left.
        (0, int(h * 0.58), int(w * 0.48), h),
        # Seal/logo area in the lower-right.
        (int(w * 0.88), int(h * 0.84), w, h),
    ]
    for box in cleanup_boxes:
        draw.rectangle(box, fill=(255, 255, 255))


def make_debug_overlay(background, data):
    overlay = background.convert("RGBA")
    draw = ImageDraw.Draw(overlay, "RGBA")
    font = load_font(18)
    small_font = load_font(14)

    for building in data["buildings"]:
        x, y, w, h = building["rect"]
        px = x * TILE
        py = y * TILE
        pw = w * TILE
        ph = h * TILE
        is_gate = "门" in building["name"]
        fill = (80, 180, 255, 70) if is_gate else (255, 70, 70, 70)
        outline = (40, 130, 255, 210) if is_gate else (255, 30, 30, 210)
        draw.rectangle((px, py, px + pw, py + ph), fill=fill, outline=outline, width=3)

        text = building["name"]
        use_font = small_font if len(text) > 5 else font
        bbox = draw.textbbox((0, 0), text, font=use_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = px + max(2, (pw - tw) // 2)
        ty = py + max(2, (ph - th) // 2)
        draw.rectangle((tx - 3, ty - 3, tx + tw + 3, ty + th + 3), fill=(0, 0, 0, 150))
        draw.text((tx, ty - 2), text, fill=(255, 255, 255, 240), font=use_font)

    overlay.save(OUT_DEBUG)


def main():
    source = find_source()
    data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    rows = len(data["tiles"])
    cols = len(data["tiles"][0])
    target_size = (cols * TILE, rows * TILE)

    image = Image.open(source).convert("RGB")
    cropped = image.crop(auto_crop_box(image))
    background = cropped.resize(target_size, Image.Resampling.LANCZOS)
    clean_non_map_content(background)
    background.save(OUT_BG)

    data = set_background_path()
    make_debug_overlay(background, data)
    print(f"source: {source}")
    print(f"background: {OUT_BG} {target_size}")
    print(f"debug overlay: {OUT_DEBUG}")


if __name__ == "__main__":
    main()
