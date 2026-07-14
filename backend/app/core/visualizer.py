from io import BytesIO
from pathlib import Path

from PIL import ImageDraw, ImageFont

from app.core.image_io import read_image


def draw_detections(image_path: str | Path, results: list[dict], extension: str = "jpg") -> bytes:
    image = read_image(image_path)
    draw = ImageDraw.Draw(image)
    font = load_font()
    for item in results:
        x1 = float(item["bbox_x"])
        y1 = float(item["bbox_y"])
        x2 = x1 + float(item["bbox_w"])
        y2 = y1 + float(item["bbox_h"])
        label = f'{item["class_name_cn"]} {item["confidence"]:.4f}'
        draw.rectangle((x1, y1, x2, y2), outline="#2E7D32", width=3)
        left, top, right, bottom = draw.textbbox((x1, y1), label, font=font)
        draw.rectangle((left, top, right + 8, bottom + 6), fill="#2E7D32")
        draw.text((x1 + 4, y1 + 2), label, fill="#FFFFFF", font=font)
    buffer = BytesIO()
    format_name = "JPEG" if extension.lower() in {"jpg", "jpeg"} else extension.upper()
    image.save(buffer, format=format_name)
    return buffer.getvalue()


def load_font():
    font_candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for candidate in font_candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), 18)
    return ImageFont.load_default()
