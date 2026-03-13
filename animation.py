import pygame
from colors import *
from grid import Vec2
from statemachine import *

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
        if not self.frames : return None
        return self.frames[min(self.index, len(self.frames) - 1)]
    
class MoveAnimation:

    def __init__(self, frames , pawn, start_tile, end_tile, duration=0.2):

        self.pawn = pawn
        self.frames = frames

        self.start = Vec2(start_tile.x,start_tile.y)
        self.end = Vec2(end_tile.x,end_tile.y)

        self.duration = duration
        self.time = 0

    def reset(self):
        self.time = 0

    def update(self, dt):

        self.time += dt

        t = min(self.time / self.duration, 1)

        # 线性插值
        x = self.start.x + (self.end.x - self.start.x) * t
        y = self.start.y + (self.end.y - self.start.y) * t

        self.pawn.render_pos = Vec2(x, y)
        # print(self.pawn.render_pos)

        if t >= 1:return True

        return False

    # def update(self, dt):
    #     self.time += dt
    #     alpha = min(self.time / self.duration, 1)

    #     self.pawn.render_pos = Vec2(                          # ✅ 用 Vec2 分量插值
    #         self.start.x * (1 - alpha) + self.end.x * alpha,
    #         self.start.y * (1 - alpha) + self.end.y * alpha
    #     )

    #     if alpha >= 1:
    #         self.pawn.position = self.end
    #         self.pawn.state_machine.change(IdleState(self.pawn))
    
    def get_frame(self):
        return self.pawn.get_sprite()
