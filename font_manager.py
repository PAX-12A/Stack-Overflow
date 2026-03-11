# font_manager.py
import pygame

_font_cache = {}
_default_name = "DOS"
_default_size = 16

def get_font(name: str = None, size: int = None):
    name = name or _default_name
    size = size or _default_size

    key = (name, size)
    if key not in _font_cache:        
        font_path = {
            "Lolita": "assets/fonts/Lolita.ttf",
            "Pixel": "assets/fonts/Pixel.ttf",
            "DOS": "assets/fonts/DOS.ttf",
            "Cogmind": "assets/fonts/Cogmind.ttf",
            "Time": "assets/fonts/Time.ttf",
            "Patriot": "assets/fonts/Patriot.ttf",
            "AA":"assets/fonts/Saitamaar-Regular.ttf",
            # "AA2":"assets/fonts/Saitamaar.woff2",
        }.get(name)

        if not font_path:
            raise ValueError(f"No font mapping for:{name}")

        _font_cache[key] = pygame.font.Font(font_path, size)

    return _font_cache[key]