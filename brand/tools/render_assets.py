"""Render the approved OpenSparklink SVG assets. Requires pymupdf and pillow."""

from pathlib import Path
import json
import shutil

import pymupdf
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
COLORS = json.loads((ROOT / "colors.json").read_text())["colors"]


def render(path, size):
    document = pymupdf.open(path)
    page = document[0]
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(size / page.rect.width, size / page.rect.height), alpha=True)
    return Image.frombytes("RGBA", (pixmap.width, pixmap.height), pixmap.samples)


for size in (32, 64, 128, 256, 512, 1024):
    image = render(ASSETS / "logo.svg", size)
    name = "avatar.png" if size == 1024 else f"avatar-{size}.png"
    image.save(ASSETS / name)
render(ASSETS / "mark.svg", 1024).save(ASSETS / "mark.png")
shutil.copyfile(ASSETS / "banner.svg", ROOT.parent / "profile/assets/banner.svg")


def font(size):
    for candidate in ("DejaVuSans.ttf", "Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


background = COLORS["background"]["hex"]
foreground = COLORS["foreground"]["hex"]
board = Image.new("RGB", (1440, 920), background)
draw = ImageDraw.Draw(board)
draw.text((56, 38), "OpenSparklink", font=font(46), fill=foreground)
draw.text((56, 103), "OS MONOGRAM / SPARK ORANGE / BRAND 1.0", font=font(19), fill=COLORS["accent"]["hex"])
large = render(ASSETS / "logo.svg", 560)
board.paste(large, (32, 180), large)

draw.text((650, 199), "Brand colors", font=font(30), fill=foreground)
for index, (key, label) in enumerate((("primary", "Spark orange"), ("accent", "Warm gold"), ("background", "Ink plum"), ("foreground", "Warm white"))):
    x = 650 + (index % 2) * 350
    y = 263 + (index // 2) * 143
    color = COLORS[key]["hex"]
    draw.rectangle((x, y, x + 285, y + 52), fill=color)
    if key == "background":
        draw.rectangle((x, y, x + 285, y + 52), outline=COLORS["accent"]["hex"], width=1)
    draw.text((x, y + 64), label + "  " + color, font=font(19), fill=foreground)

draw.text((650, 580), "Avatar sizes", font=font(30), fill=foreground)
for size, x in ((128, 650), (64, 850), (32, 984)):
    image = render(ASSETS / "logo.svg", size)
    board.paste(image, (x, 642), image)
    draw.text((x, 792), f"{size} px", font=font(19), fill=foreground)
circle = render(ASSETS / "logo.svg", 128)
mask = Image.new("L", (128, 128), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 127, 127), fill=255)
board.paste(circle, (1140, 642), mask)
draw.text((1140, 792), "Circle crop", font=font(19), fill=foreground)
draw.text((56, 858), "Adopted 2026-11-16  /  github.com/OpenSparklink/.github/tree/main/brand", font=font(18), fill=foreground)
board.save(ASSETS / "brand-board.png")
print("Rendered six avatar sizes, transparent PNG, brand board and profile banner mirror.")
