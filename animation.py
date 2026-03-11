import pygame
from colors import *

class AnimationController:
    def __init__(self, pawn):
        self.pawn = pawn
        self.current = None
        self.default = None

    def play(self, anim):
        self.current = anim
        anim.reset()

    def update(self, dt):
        if self.current:
            finished = self.current.update(dt)
            if finished:
                self.current = None

    def get_frame(self):
        if self.current:
            return self.current.get_frame()
        elif self.default:
            return self.default.get_frame()
        return self.pawn.get_sprite()
    
class FrameAnimation:
    def __init__(self, frames, speed=0.1, loop=False):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.time = 0
        self.index = 0

    def reset(self):
        self.time = 0
        self.index = 0

    def update(self, dt):
        self.time += dt
        if self.time >= self.speed:
            self.time = 0
            self.index += 1

            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    return True  # finished

        return False

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[min(self.index, len(self.frames) - 1)]
