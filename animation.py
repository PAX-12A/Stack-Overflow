import pygame

class FrameAnimation:
    def __init__(self, frames, frame_duration, loop=False):
        """
        frames: [Surface, Surface, ...]
        frame_duration: 每帧毫秒
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop

        self.start_time = pygame.time.get_ticks()
        self.finished = False

        self.current_frame = self.frames[0]

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        frame_count = len(self.frames)
        index = elapsed // self.frame_duration

        if not self.loop and index >= frame_count:
            self.finished = True
            index = frame_count - 1

        self.current_frame = self.frames[index % frame_count]

    def draw(self, screen, pos):
        screen.blit(self.current_frame, pos)


class SlashAttackAnimation(FrameAnimation):
    def __init__(self, frames, center_pos, direction, frame_duration=60):
        super().__init__(frames, frame_duration, loop=False)

        self.center_pos = center_pos
        self.direction = direction

    def draw(self, screen):
        img = self.current_frame

        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)

        rect = img.get_rect(center=self.center_pos)
        screen.blit(img, rect)

