from grid import Vec2
from util import load_image
from events import *


class Entity:
    def __init__(self, scene, position):
        self.scene = scene
        self.position = position
        self.alive = True

    def update(self):
        pass

    def draw(self):
        pass

class Projectile(Entity):

    def __init__(self,scene,projectile_type,position,direction,movement,collision,lifetime,health = 1):
        super().__init__(scene, position)

        self.direction = direction

        self.movement = movement
        self.collision = collision
        self.lifetime = lifetime
        self.projectile_type = projectile_type
        self.health = 1 
        self.name = "P"
        self.sprite = load_image(
            "arts/sprite/Projectile/Arrow.png",
            (32,32))

    def update(self):

        self.movement.update(self)

        self.collision.update(self)

        self.lifetime.update(self)

    def get_sprite(self):
        return self.sprite

    def draw(self, screen):

        screen_pos = self.scene.camera.apply(
            self.position
        )

        screen.blit(
            self.sprite,
            screen_pos
        )
    def die(self):
        print("Projectile died")


class StraightMovement:

    def update(self, projectile):

        projectile.position += Vec2(
            projectile.direction,
            0
        )

class DamageCollision:

    def __init__(self, damage):
        self.damage = damage

    def update(self, projectile):

        for e in projectile.scene.enemies:

            if e.position == projectile.position:

                projectile.scene.events.push(DamageEvent(projectile,e,self.damage))
                projectile.scene.events.push(DamageEvent(projectile,projectile,self.damage))#自毁

                projectile.alive = False

                return
        if projectile.scene.player.position == projectile.position:
            projectile.scene.events.push(DamageEvent(projectile,projectile.scene.player,self.damage))
            projectile.scene.events.push(DamageEvent(projectile,projectile,self.damage))
            projectile.alive = False

            

class Lifetime:

    def __init__(self, turns):
        self.turns = turns

    def update(self, projectile):

        self.turns -= 1

        if self.turns <= 0:
            projectile.alive = False

class Arrow(Projectile):

    def __init__(self,scene,position,direction,damage):

        super().__init__(
            scene,
            "Arrow",
            position,
            direction,
            movement=StraightMovement(),

            collision=DamageCollision(
                damage
            ),

            lifetime=Lifetime(5)
        )


class ProjectileFactory:

    def create(
        self,
        projectile_type,
        actor,
        damage
    ):

        if projectile_type == "Arrow":

            return Arrow(
                actor.scene,
                actor.position,
                actor.direction,
                damage
            )


projectile_registry = {
    "Arrow": Arrow,
    # "Fireball": Fireball
}

# PROJECTILE_SPRITES = {
#     "Arrow": load_image("arts/sprite/Projectile/Arrow.png", (32, 32)),
#     # "Fireball": load_image(...),
# }