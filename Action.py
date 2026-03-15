from grid import Vec2
from statemachine import *
class Action:

    def __init__(self, actor):
        self.actor = actor

    def start(self, scene):
        pass

    def update(self, scene, dt):
        pass

    def is_finished(self):
        return True

class MoveAction(Action):

    def __init__(self, actor, offset):

        super().__init__(actor)

        self.offset = offset
        self.finished = False
        self.target = None

    def start(self, scene):

        self.actor.move_completed = False     # ← 出发前清除旗子

        old_pos = self.actor.position
        new_pos = old_pos + self.offset

        if not self.actor.move(self.offset):
            self.finished = True
            return
        
        self.target = new_pos


    def update(self, scene, dt):

        if self.finished:
            return

        if self.actor.move_completed:         # ← 检查旗子，不检查 position
            self.actor.move_completed = False
            self.finished = True

    def is_finished(self):
        return self.finished

class AttackAction(Action):

    def __init__(self, actor, weapon, damage):
        super().__init__(actor)

        self.weapon = weapon
        self.damage = damage
        self.finished = False

    def start(self, scene):

        self.actor.attack_completed = False

        self.weapon.execute(scene, self.actor, self.damage)

    def update(self, scene, dt):

        if self.finished:
            return

        if self.actor.attack_completed:         
            self.actor.attack_completed = False
            self.finished = True

    def is_finished(self):
        
        return self.finished
    
class MineAction(Action):
    def __init__(self, actor , weapon):
        super().__init__(actor)
        self.finished = False
        self.weapon= weapon

    def start(self, scene):
        for pt in self.weapon.pattern :
            scene.mymap.destroy_tile(self.actor.position + pt)
        self.finished = True

    def is_finished(self):
        return self.finished

class GravityAction(Action):
    def __init__(self, actor):
        super().__init__(actor)
        self.inner_action = None
        self.finished = False

    def start(self, game):
        if not game.mymap.is_walkable(self.actor.position):
            self.inner_action = MoveAction(self.actor, Vec2(0, 1))
            self.inner_action.start(game)   # ← 直接启动，不进主队列
        else:
            self.finished = True

    def update(self, scene, dt):
        if self.inner_action:
            self.inner_action.update(scene, dt)
            if self.inner_action.is_finished():
                self.finished = True
        
    def is_finished(self):
        return self.finished
    
class ParallelAction(Action):
    """包裹一组 Action，让它们同时执行，全部完成后才结束"""

    def __init__(self, actions: list[Action]):
        super().__init__(None)  # 没有单一 actor
        self.parallel_actions = actions

    def start(self, scene):
        for action in self.parallel_actions:
            action.start(scene)

    def update(self, scene, dt):
        for action in self.parallel_actions:
            if not action.is_finished():
                action.update(scene, dt)

    def is_finished(self):
        return all(action.is_finished() for action in self.parallel_actions)