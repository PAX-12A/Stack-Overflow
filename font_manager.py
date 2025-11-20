# font_manager.py
import pygame

_font_cache = {}
_current_lang = "en"
_default_name = "DOS"
_default_size = 16

def set_lang(lang: str):
    global _current_lang
    _current_lang = lang
    # 切换语言时可以清空 cache 或保持复用
    # _font_cache.clear()

def set_default_font(name: str, size: int = 16):
    global _default_name, _default_size
    _default_name = name
    _default_size = size

def get_font(name: str = None, size: int = None):
    lang = _current_lang
    name = name or _default_name
    size = size or _default_size

    key = (lang, name, size)
    if key not in _font_cache:
        # if lang == "ch":
        #     font_path = {
        #         "Lolita": "assets/fonts/Lolita.ttf",
        #         "Pixel": "assets/fonts/Pixel.ttf",
        #     }.get(name)
        # elif lang == "en":
        #     font_path = {
        #         "DOS": "assets/fonts/DOS.ttf",
        #         "Cogmind": "assets/fonts/Cogmind.ttf",
        #         "Time": "assets/fonts/Time.ttf",
        #         "Patriot": "assets/fonts/Patriot.ttf",
        #     }.get(name)
        # else:
        #     raise ValueError(f"Unsupported language: {lang}, name: {name}")
        
        font_path = {
            "Lolita": "assets/fonts/Lolita.ttf",
            "Pixel": "assets/fonts/Pixel.ttf",
            "DOS": "assets/fonts/DOS.ttf",
            "Cogmind": "assets/fonts/Cogmind.ttf",
            "Time": "assets/fonts/Time.ttf",
            "Patriot": "assets/fonts/Patriot.ttf",
            "AA":"assets/fonts/Saitamaar-Regular.ttf",
        }.get(name)

        if not font_path:
            raise ValueError(f"No font mapping for {lang}:{name}")

        _font_cache[key] = pygame.font.Font(font_path, size)

    return _font_cache[key]
