#!/usr/bin/env python3
"""
Generate a real animated terminal-style ASCII profile GIF from a GitHub avatar.

The generated GIF is intentionally used in the README instead of animated SVG:
GitHub documents that SVG animation is not supported when viewing repository
SVGs, while GIF is a supported image format.

Environment:
  GITHUB_USERNAME=pranavtdhote
  PROFILE_IMAGE_URL=optional custom image URL
"""

import os
import urllib.request
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont

USERNAME = os.getenv("GITHUB_USERNAME", "pranavtdhote")
IMAGE_URL = os.getenv("PROFILE_IMAGE_URL", f"https://github.com/{USERNAME}.png")

OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

COLS = 62
ROWS = 30
FONT_SIZE = 13
CELL_W = 8
CELL_H = 14

RAMP = " .:-=+*#%@"
BG = (5, 11, 16)
FG = (0, 201, 255)
MUTED = (128, 160, 170)
GREEN = (63, 185, 80)
WHITE = (220, 235, 240)

def font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/CascadiaMono.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, FONT_SIZE)
    return ImageFont.load_default()

FONT = font()

def get_image():
    req = urllib.request.Request(
        IMAGE_URL,
        headers={"User-Agent": "pranav-github-profile-generator"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return Image.open(BytesIO(response.read())).convert("RGB")

def make_ascii(img):
    img = ImageOps.fit(img, (COLS, ROWS), method=Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)

    pixels = list(gray.getdata())
    rows = []

    for y in range(ROWS):
        line = []
        for x in range(COLS):
            value = pixels[y * COLS + x]
            # Dark pixels = dense characters, bright pixels = whitespace.
            idx = int((255 - value) / 255 * (len(RAMP) - 1))
            line.append(RAMP[idx])
        rows.append("".join(line))

    return rows

def text(draw, xy, value, fill=WHITE, anchor=None):
    draw.text(xy, value, font=FONT, fill=fill, anchor=anchor)

def build_frame(rows, reveal_rows, cursor_on=True, final=False):
    width = 1180
    height = 520
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Window / terminal chrome.
    draw.rounded_rectangle((18, 18, width-18, height-18), radius=16, outline=(35, 55, 65), width=2)
    draw.rectangle((19, 19, width-19, 55), fill=(10, 18, 24))

    draw.ellipse((36, 32, 47, 43), fill=(248, 81, 73))
    draw.ellipse((55, 32, 66, 43), fill=(255, 193, 7))
    draw.ellipse((74, 32, 85, 43), fill=(63, 185, 80))
    text(draw, (width//2, 36), "pranav@github: ~", fill=MUTED, anchor="mm")

    # ASCII portrait.
    x0, y0 = 34, 78
    for i in range(min(reveal_rows, len(rows))):
        text(draw, (x0, y0 + i * CELL_H), rows[i], fill=FG)

    # Right terminal info.
    px = 570
    y = 90
    text(draw, (px, y), "pranav@github", fill=GREEN)
    text(draw, (px + 132, y), ":~$ ./profile", fill=WHITE)
    y += 32

    info = [
        ("NAME", "Pranav Dhote"),
        ("ROLE", "Full-Stack Engineer"),
        ("FOCUS", "AI / GenAI / Web3"),
        ("EDUCATION", "B.Tech Information Technology"),
        ("LOCATION", "Pune, Maharashtra"),
        ("STATUS", "BUILDING + SHIPPING"),
        ("STACK", "React • Node • Python • Java"),
        ("INTERESTS", "AI Agents • NLP • DSA"),
    ]

    for key, value in info:
        text(draw, (px, y), f"{key:<11}", fill=(255, 166, 87))
        text(draw, (px + 112, y), value, fill=(165, 214, 255))
        y += 28

    y += 12
    text(draw, (px, y), "──────────────────────────────────", fill=MUTED)
    y += 28
    text(draw, (px, y), "GITHUB", fill=GREEN)
    y += 28
    text(draw, (px, y), "github.com/pranavtdhote", fill=WHITE)
    y += 34

    prompt = "pranav@github:~$ "
    text(draw, (px, y), prompt, fill=GREEN)
    cursor_x = px + draw.textlength(prompt, font=FONT)
    if cursor_on:
        draw.rectangle((cursor_x, y-2, cursor_x+8, y+14), fill=GREEN)

    return img

def main():
    avatar = get_image()
    rows = make_ascii(avatar)

    frames = []
    # Type the portrait line-by-line.
    for n in range(0, len(rows) + 1):
        frames.append(build_frame(rows, n, cursor_on=True))
        if n > 0:
            frames.append(build_frame(rows, n, cursor_on=False))

    # Final terminal cursor blink frames.
    for _ in range(5):
        frames.append(build_frame(rows, len(rows), cursor_on=True, final=True))
        frames.append(build_frame(rows, len(rows), cursor_on=False, final=True))

    frames[0].save(
        OUT / "neofetch-terminal.gif",
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=False,
    )

    print("Generated assets/neofetch-terminal.gif")

if __name__ == "__main__":
    main()
