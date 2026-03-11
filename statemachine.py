from animation import *
from events import DamageEvent
from vfxsystem import SlashVFX
class StateMachine:
    def __init__(self, owner):
        self.owner = owner
        self.state = None

    def change(self, new_state):
        
        if self.state and type(self.state) == type(new_state):
            return
        # print("STATE CHANGE", self.owner.name, type(new_state))
        if self.state:
            self.state.exit()

        self.state = new_state
        self.state.enter()

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
        self.pawn.anim.play(
            FrameAnimation(self.pawn.idle_frames, loop=True)
        )

    def update(self, dt):
        pass

class AttackState(State):

    def __init__(self, pawn, attack_positions,damage):
        super().__init__(pawn)
        self.attack_positions=attack_positions
        self.damage = damage
        self.hit_done = False

    def enter(self):
        print(f"{self.pawn.name} Enter Attack State")
        self.anim = FrameAnimation(
            self.pawn.attack_frames,
            speed=0.08
        )
        self.pawn.anim.play(self.anim)

    def update(self, dt):

        finished = self.anim.update(dt)

        # 在第3帧造成伤害
        # print(self.anim.index)
        if self.anim.index >= 0 and not self.hit_done:

            self.hit_done = True
                #self.apply_weapon_effects(target, weapon)
            for pos in self.attack_positions:
                self.pawn.events.push(
                    DamageEvent(self.pawn, self.pawn.scene.get_pawn_at(pos), self.damage)
                )    
                self.pawn.vfx.add(
                    SlashVFX(
                        self.pawn.slash_frames,
                        self.pawn.get_cell_center(pos),
                        self.pawn.direction
                    )
                )

        if finished:
            print(f"{self.pawn.name} Exit Attack State")
            self.pawn.scene.finish_action()
            self.pawn.state_machine.change(
                IdleState(self.pawn)
            )

class MoveState(State):

    def __init__(self, pawn, target_pos):
        super().__init__(pawn)
        self.start = pawn.position
        self.target = target_pos
        self.duration = 0.2
        self.t = 0

    def enter(self):
        pass

    def update(self, dt):

        self.t += dt
        alpha = min(self.t / self.duration, 1)

        self.pawn.render_x = (
            self.start*(1-alpha) + self.target*alpha
        )

        if alpha >= 1:
            self.pawn.position = self.target
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