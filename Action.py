from grid import Vec2
from statemachine import *
class Action:

    def __init__(self, actor ,turn_consumed = False):
        self.actor = actor
        self.turn_consumed = turn_consumed #是否花费玩家回合

    def start(self, scene):
        pass

    def update(self, scene, dt):
        pass

    def is_finished(self):
        return True



# class MoveAction(Action):

#     def __init__(self, actor, offset):

#         super().__init__(actor)

#         self.offset = offset
#         self.finished = False
#         self.target = None

#     def start(self, scene):

#         self.actor.move_completed = False     # ← 出发前清除旗子

#         old_pos = self.actor.position
#         new_pos = old_pos + self.offset

#         result = self.actor.move(self.offset)

#         if result is None:
#             self.finished = True
#             return

#         old_pos, new_pos = result
        
#         self.target = new_pos
#         # self.render_pos = old_pos

#         step = TimelineStep(
#             actor_id=self.actor.actor_id,
#             step_type="move",
#             start=old_pos,
#             end=new_pos,
#             duration=0.15
#         )

#         scene.timeline.append(step)


#     def update(self, scene, dt):

#         if self.finished:
#             return

#         if self.actor.move_completed:         # ← 检查旗子，不检查 position
#             self.actor.move_completed = False
#             self.finished = True

#     def is_finished(self):
#         return self.finished

class WaitAction(Action):
    def __init__(self, actor):
        super().__init__(actor,turn_consumed=True)
    def start(self, scene):
        print("waiting")
        return
        


class MoveAction(Action):

    def __init__(self, actor, offset):

        super().__init__(actor,turn_consumed=True)

        self.offset = offset
        self.finished = False

    def start(self, scene):

        old_pos = self.actor.position
        new_pos = old_pos + self.offset


        result = self.actor.move(self.offset) # 逻辑移动

        if result is None:

            self.turn_consumed = False
            self.finished = True

            return

        # Timeline
        step = TimelineStep(
            actor_id=self.actor.actor_id,
            step_type="move",

            start=old_pos,
            end=new_pos,

            duration=0.15
        )

        scene.timeline.append(step)

        # 视觉动画
        self.actor.state_machine.change(
            MoveVisualState(
                self.actor,
                step
            )
        )

        # Trap
        trap = scene.mymap.get_trap(new_pos)

        if trap:
            trap.on_enter(self.actor)

        self.finished = True

    def update(self, scene, dt):
        pass

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

# class GravityAction(Action):
#     def __init__(self, actor):
#         super().__init__(actor)
#         self.inner_action = None
#         self.finished = False

#     def start(self, game):
#         if not game.mymap.is_walkable(self.actor.position):
#             self.inner_action = MoveAction(self.actor, Vec2(0, 1))
#             self.inner_action.start(game)   # ← 直接启动，不进主队列
#         else:
#             self.finished = True

#     def update(self, scene, dt):
#         # if self.inner_action:
#         #     self.inner_action.update(scene, dt)
#         #     if self.inner_action.is_finished():
#                 self.finished = True
        
#     def is_finished(self):
#         return self.finished

class GravityAction(Action):

    def __init__(self, actor):

        super().__init__(actor)

        self.finished = False

    def start(self, scene):

        old_pos = self.actor.position
        new_pos = old_pos

        new_pos = old_pos + Vec2(0,1)
        self.actor.position = new_pos
        if scene.mymap.is_walkable(new_pos):
            scene.events.push(DamageEvent(None,self.actor,1)) #test,临时模拟摔落伤害

        step = TimelineStep(
            actor_id=self.actor.actor_id,
            step_type="fall",
            start=old_pos,
            end=new_pos,
            duration=0.1
        )

        scene.timeline.append(step)

        self.actor.state_machine.change(
            MoveVisualState(
                self.actor,
                step
            )
        )

        self.finished = True

    def update(self, scene, dt):
        pass

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


import json   
class TimelineStep:

    def __init__(self,actor_id,step_type,start,end,duration=0.15,):

        self.actor_id = actor_id
        self.step_type = step_type

        self.start = start
        self.end = end

        self.duration = duration

    
    def to_dict(self):

        return {
            "actor_id": self.actor_id,
            "step_type": self.step_type,

            "start": [
                self.start.x,
                self.start.y
            ],

            "end": [
                self.end.x,
                self.end.y
            ],

            "duration": self.duration
        }

