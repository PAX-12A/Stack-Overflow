import pygame


class Camera:

    def __init__(self, screen_width, screen_height, map_width, map_height, tile_size):

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.tile_size = tile_size

        # 地图像素大小
        self.map_pixel_width = map_width * tile_size
        self.map_pixel_height = map_height * tile_size

        # camera位置（世界坐标）
        self.x = 0
        self.y = 0


    def update(self, target):

        # 玩家世界坐标
        target_x = target.render_pos.x * self.tile_size
        target_y = target.render_pos.y * self.tile_size

        # 目标camera位置（让玩家居中）
        self.x = target_x - self.screen_width // 2
        self.y = target_y - self.screen_height // 2

        # 防止camera超出地图

        self.x = max(0, min(self.x, self.map_pixel_width - self.screen_width))
        self.y = max(0, min(self.y, self.map_pixel_height - self.screen_height))


    def apply(self, world_pos):

        """世界坐标 → 屏幕坐标"""

        return (
            world_pos[0] - self.x,
            world_pos[1] - self.y
        )


    def apply_rect(self, rect):

        """Rect版本"""

        return pygame.Rect(
            rect.x - self.x,
            rect.y - self.y,
            rect.width,
            rect.height
        )