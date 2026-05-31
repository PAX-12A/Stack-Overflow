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

    def __init__(self,scene,projectile_type,position,direction,movement,collision,lifetime, health = 1,speed = 1):
        super().__init__(scene, position)

        self.direction = direction

        self.movement = movement
        self.collision = collision
        self.lifetime = lifetime
        self.projectile_type = projectile_type
        self.health = health 
        self.name = projectile_type
        self.speed = speed
        self.sprite = scene.spritemanager.get(self.projectile_type)

    def update(self):

        self.collision.update(self)

        self.movement.update(self,self.speed)

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

    def update(self, projectile, speed = 1):

        projectile.position += projectile.direction*speed

class DamageCollision:

    def __init__(self, damage):
        self.damage = damage

    def update(self, projectile):

        for e in projectile.scene.enemies:

            if e.position == projectile.position:

                projectile.scene.events.push(DamageEvent(projectile,e,self.damage))
                projectile.scene.events.push(DamageEvent(None,projectile,self.damage))#自毁

                projectile.alive = False

                return
        if projectile.scene.player.position == projectile.position:
            projectile.scene.events.push(DamageEvent(projectile,projectile.scene.player,self.damage))
            projectile.scene.events.push(DamageEvent(None,projectile,self.damage))
            projectile.alive = False

            

class Lifetime:

    def __init__(self, turns):
        self.turns = turns

    def update(self, projectile):

        self.turns -= 1

        if self.turns <= 0:
            projectile.scene.events.push(DamageEvent(None,projectile,projectile.health))#自毁

class Arrow(Projectile):

    def __init__(self,scene,projectile_type,position,direction,damage,lifetime=5,speed=1):

        super().__init__(scene,projectile_type,position,direction,speed=speed,
                         
            movement=StraightMovement(),

            collision=DamageCollision(damage),

            lifetime=Lifetime(lifetime)
        )

projectile_registry = {
    "Arrow": Arrow,
    "Mana": Arrow,
    "Bullet": Arrow,
}

projectile_info = {

    "Arrow": {

        "movement": "straight",

        "collision": "damage",

        "sprite": "Arrow",

        "health": 1
    },

    "Mana": {

        "movement": "straight",

        "collision": "damage",

        "sprite": "Mana",

        "health": 1
    },

    "Bullet": {

        "movement": "straight",

        "collision": "damage",

        "sprite": "Bullet",

        "health": 1
    },

    "Missile": {

        "movement": "homing",

        "collision": "explosion",

        "sprite": "Missile",

        "health": 1
    }
}
