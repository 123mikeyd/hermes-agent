#!/usr/bin/env python
"""Create labeled contact sheets from Blender-style numbered PNG frames.

Usage:
  python contact_sheet.py FRAMES_DIR OUTPUT.jpg 71 72 73 74 80 88
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__.strip())
        return 2
    frames_dir = Path(sys.argv[1])
    output = Path(sys.argv[2])
    frames = [int(value) for value in sys.argv[3:]]
    thumb_w, thumb_h, label_h, cols = 320, 180, 24, 4
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        path = frames_dir / f"frame_{frame:04d}.png"
        image = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(8, 8, 8))
        draw.text((x + 8, y + thumb_h + 5), f"frame {frame}", fill=(255, 255, 255))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
