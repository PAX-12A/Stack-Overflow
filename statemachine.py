from animation import FrameAnimation,MoveAnimation
from events import DamageEvent
from vfxsystem import SlashVFX
from grid import Vec2

HIT_FRAME = 0  # 在第几帧触发伤害

class StateMachine:
    def __init__(self, owner):
        self.owner = owner
        self.state = None

    def change(self, new_state):
        
        if self.state:
            self.state.exit() #退出旧状态

        self.state = new_state
        self.state.enter() #进入新状态

    def update(self, dt):
        if self.state:
            self.state.update(dt)

class State:
    def __init__(self, pawn):
        self.pawn = pawn

    def enter(self):
        pass

    def update(self, dt):
        pass

    def exit(self):
        pass

class IdleState(State):

    def enter(self):
        self.anim = FrameAnimation(self.pawn.idle_frames, 0.5 ,loop=True)
        self.pawn.anim.play(self.anim)

    def update(self, dt):
        pass

class AttackState(State):

    def __init__(self, pawn, attack_positions , damage):
        super().__init__(pawn)
        self.attack_positions=attack_positions
        self.damage = damage
        self.hit_done = False
        self.pawn.attack_completed = False   

    def enter(self):
        print(f"{self.pawn.name} Enter Attack State")
        self.anim = FrameAnimation(
            self.pawn.attack_frames,
            speed=0.08
        )
        self.pawn.anim.play(self.anim)

    def update(self, dt):
        if self.anim.finished:
            self.pawn.attack_completed = True   
            self.pawn.state_machine.change(IdleState(self.pawn)) 

        if self.anim.index >= HIT_FRAME and not self.hit_done:  # 等到指定帧
            self.hit_done = True
            for pos in self.attack_positions:
                target = self.pawn.scene.get_pawn_at(pos)
                if target:
                    self.pawn.events.push(DamageEvent(self.pawn, target, self.damage))
                    self.pawn.vfx.add(
                    SlashVFX(
                        self.pawn.slash_frames,
                        target.render_pos,
                        self.pawn.direction
                    )
                )

# class MoveState(State):

#     def __init__(self, pawn, old_pos , new_pos ):
#         super().__init__(pawn)
#         self.start = Vec2(float(pawn.render_pos.x), float(pawn.render_pos.y))  # 用渲染位置
#         # self.start = pawn.position 
#         self.duration = 0.2
#         self.t = 0
#         self.old_pos = old_pos
#         self.new_pos = new_pos

#     def enter(self):
#         self.anim = MoveAnimation(self.pawn.idle_frames, self.pawn, self.old_pos, self.new_pos)
#         self.pawn.anim.play(self.anim)

#     def update(self, dt):
#         if self.anim.finished:
#             self.pawn.move_completed = True        
#             self.pawn.position = self.new_pos

#             # 落地后检查陷阱
#             trap = self.pawn.scene.mymap.get_trap(self.new_pos)
#             if trap:
#                 trap.on_enter(self.pawn)   # ← 陷阱自己决定效果

#             self.pawn.state_machine.change(IdleState(self.pawn))

class MoveVisualState(State):

    def __init__(self, pawn, step):

        super().__init__(pawn)

        self.step = step

    def enter(self):

        self.anim = MoveAnimation(
            self.pawn.idle_frames,

            self.pawn,

            self.step.start,
            self.step.end,

            self.step.duration
        )

        self.pawn.anim.play(self.anim)

    def update(self, dt):

        if self.anim.finished:

            self.pawn.state_machine.change(
                IdleState(self.pawn)
            )

class HitState(State):

    def enter(self):

        self.anim = FrameAnimation(
            self.pawn.hit_frames
        )

        self.pawn.anim.play(self.anim)

    def update(self, dt):

        if self.anim.update(dt):
            self.pawn.state_machine.change(
                IdleState(self.pawn)
            )