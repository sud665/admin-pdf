import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontManager:
    def __init__(self, font_dir: str = "fonts"):
        self.font_dir = font_dir
        self.registered_fonts: set[str] = set()

    def register_font(self, font_name: str, font_filename: str) -> str:
        font_path = os.path.join(self.font_dir, font_filename)
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        if font_name not in self.registered_fonts:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            self.registered_fonts.add(font_name)
        return font_name
