from animation import *
class VFXSystem:

    def __init__(self):
        self.effects = []

    def add(self, effect):
        self.effects.append(effect)

    def update(self, dt):

        for effect in self.effects[:]:

            finished = effect.update(dt)

            if finished:
                self.effects.remove(effect)

    def draw(self, screen):

        for effect in self.effects:
            effect.draw(screen)

class VFX:

    def update(self, dt):
        return False

    def draw(self, screen):
        pass

class SlashVFX(VFX):

    def __init__(self, frames, center_pos, direction):

        self.anim = FrameAnimation(
            frames,
            speed=0.06,
            loop=False
        )
        

        self.center_pos = center_pos
        self.direction = direction

    def update(self, dt):
        return self.anim.update(dt)

    def draw(self, screen):

        img = self.anim.get_frame()

        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)

        rect = img.get_rect(center=self.center_pos)

        screen.blit(img, rect)