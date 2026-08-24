import os, urllib.request
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "pranavtdhote")
URL = os.getenv("ASCII_SOURCE_URL", f"https://github.com/{USERNAME}.png")
OUT = Path("assets")
CHARS = "@%#*+=-:. "
WIDTH = 72

def download():
    p = OUT / ".avatar.png"
    req = urllib.request.Request(URL, headers={"User-Agent": "github-profile-generator"})
    with urllib.request.urlopen(req, timeout=30) as r:
        p.write_bytes(r.read())
    return p

def ascii_art(path):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise SystemExit("Pillow is required: pip install pillow")
    img = ImageOps.fit(Image.open(path).convert("L"), (WIDTH, 34))
    px = list(img.getdata())
    return [
        "".join(CHARS[p * (len(CHARS)-1) // 255] for p in px[y*WIDTH:(y+1)*WIDTH])
        for y in range(img.height)
    ]

def make_svg(lines, dark):
    bg, fg, muted = (
        ("#050b10", "#00c9ff", "#8aa7b2") if dark
        else ("#f6fbfd", "#007f9e", "#4f6972")
    )
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 780">',
        f'<rect width="900" height="780" rx="18" fill="{bg}"/>',
        f'<text x="36" y="42" fill="{fg}" font-family="monospace" font-size="18">pranav@github:~$ whoami</text>',
        f'<text x="36" y="70" fill="{muted}" font-family="monospace" font-size="13">ASCII PROFILE • AUTO GENERATED</text>',
    ]
    y = 105
    for line in lines:
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        out.append(f'<text x="36" y="{y}" fill="{fg}" font-family="monospace" font-size="12">{safe}</text>')
        y += 18
    out += [
        f'<text x="36" y="730" fill="{muted}" font-family="monospace" font-size="13">Full-Stack • AI/GenAI • Web3</text>',
        "</svg>"
    ]
    return "\n".join(out)

def main():
    OUT.mkdir(exist_ok=True)
    avatar = download()
    lines = ascii_art(avatar)
    (OUT/"ascii-profile-dark.svg").write_text(make_svg(lines, True), encoding="utf-8")
    (OUT/"ascii-profile-light.svg").write_text(make_svg(lines, False), encoding="utf-8")
    avatar.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
