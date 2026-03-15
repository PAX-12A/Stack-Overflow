from colors import *
from grid import Vec2
from Action import *
class Weapon:
    def __init__(self, name, data):
        self.name = name
        self.damage = data["damage"]
        self.pattern = data["pattern"]  # 相对于actor位置的攻击范围
        self.cooldown = data["cooldown"]
        self.current_cooldown = 0
        self.unique_in_sequence = data["unique_in_sequence"]
        self.status_effects = data.get("status_effects",None)
    
    def is_ready(self):
        return self.current_cooldown <= 0
    
    def use(self):
        if self.is_ready():
            self.current_cooldown = self.cooldown
            return True
        return False
    
    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def execute(self, scene, actor, damage):
        pass

class PatternWeapon(Weapon):

    def build_actions(self, scene, actor, damage):
        return [AttackAction(actor, self, damage)]  # 单段，直接返回一个
    
    def execute(self, scene, actor, damage):
        # 只负责攻击，移动已经由 MoveAction 处理
        scene.attack_by_pattern(actor, self, damage)

class DashWeapon(Weapon):

    def build_actions(self, scene, actor, damage):
        closest_enemy = scene.get_closestL_pawn(actor.position, actor.direction)

        if not closest_enemy:
            print(f"{actor.name}:No enemy")
            return [MoveAction(actor, Vec2(actor.direction, 0))]

        target_x = closest_enemy.position.x - actor.direction
        offset = Vec2(target_x - actor.position.x, 0)

        return [
            MoveAction(actor, offset),
            AttackAction(actor, self, damage),  # execute() 只做攻击
        ]

    def execute(self, scene, actor, damage):
        # 只负责攻击，移动已经由 MoveAction 处理
        scene.attack_by_pattern(actor, self, damage)

class RollWeapon(Weapon):

    def build_actions(self, scene, actor, damage):
        closest_enemy = scene.get_closestL_pawn(actor.position, actor.direction)

        if not closest_enemy:
            print(f"{actor.name}:No enemy")
            return [MoveAction(actor, Vec2(actor.direction, 0))]

        target_x = closest_enemy.position.x + actor.direction
        offset = Vec2(target_x - actor.position.x, 0)

        return [
            MoveAction(actor, offset),
            AttackAction(actor, self, damage),  # execute() 只做攻击
        ]

    def execute(self, scene, actor, damage):
        # 只负责攻击，移动已经由 MoveAction 处理
        scene.attack_by_pattern(actor, self, damage)

class MoveWeapon(Weapon):

    def build_actions(self, scene, actor, damage):
        act = []
        for op in self.pattern:
            if op !=Vec2(0,-1): #向上不镜像
                op = op * actor.direction
            act.append(MoveAction(actor,op))
        return act

class SwapWeapon(Weapon):

    def execute(self, scene, actor, damage):

        scene.use_swap_weapon()

class MineWeapon(Weapon):

    def build_actions(self, scene, actor, damage):
        print(6666)

        return [
            MineAction(actor,self),
            AttackAction(actor, self, damage),  # execute() 只做攻击
        ]

    def execute(self, scene, actor, damage):
        # 只负责攻击，移动已经由 MoveAction 处理
        scene.attack_by_pattern(actor, self, damage)

weapon_info = {
    "Hello World": {
        "damage": 3,
        "pattern": [Vec2(1,0)],
        "cooldown": 0,
        "unique_in_sequence": False
    },
    "Goto Jump": {
        "damage": 0,
        "pattern": [Vec2(0,-1),Vec2(0,-1)],
        "cooldown": 0,
        "unique_in_sequence": True
    },
    "DEBUG": {
        "damage": 0,
        "pattern": [Vec2(5,0)],
        "cooldown": 0,
        "unique_in_sequence": False
    },
    "DragAndDrop": {
        "damage": 0,
        "pattern": [Vec2(0,-1),Vec2(0,-1),Vec2(0,-1),Vec2(0,-1),Vec2(0,-1),Vec2(0,-1)],
        "cooldown": 4,
        "unique_in_sequence": False
    },
    "Pointer Sword": {
        "damage": 2,
        "pattern": [Vec2(1,0)],
        "cooldown": 4,
        "unique_in_sequence": True
    },
    "Template Greatsword":{
        "damage": 5,
        "pattern": [Vec2(-1,0), Vec2(1,0),Vec2(0,-1), Vec2(0,1)],
        "cooldown": 4,
        "unique_in_sequence": True
    },
    "Data Mining": {
        "damage": 2,
        "pattern": [Vec2(0,1),Vec2(-1,0),Vec2(1,0)],
        "cooldown": 4,
        "unique_in_sequence": True
    },
    "Snake Roll":{
        "damage": 2,
        "pattern": [Vec2(-1,0)],
        "cooldown": 5,
        "unique_in_sequence": True
    },
    "Snake Staff":{
        "damage": 15,
        "pattern": [2,4,6,8],
        "cooldown": 8,
        "unique_in_sequence": True
    },
    "JVM Inferno Staff": {
        "damage": 15,
        "pattern": [-2,-1,0,1,2],
        "cooldown": 7,
        "unique_in_sequence": True
    },
    "Text Rain":{
        "damage": 5,
        "pattern": [-5,-4,-3,-2,-1,1,2,3,4,5],
        "cooldown": 8,
        "unique_in_sequence": True
    },
    "Formula Barrage":{
        "damage": 10,
        "pattern": [1,2,3,4,5],
        "cooldown": 6,
        "unique_in_sequence": True
    },
    "Random Generator":{
        "damage": 6,
        "pattern": [-5,-4,-3,-2,-1,1,2,3,4,5],
        "cooldown": 4,
        "unique_in_sequence": True
    },
    "DashToDeadline":{
        "damage": 6,
        "pattern": [Vec2(1,0)],
        "cooldown": 0,
        "unique_in_sequence": False
    },
    "Exam":{
        "damage": 10,
        "pattern": [Vec2(1,0)],
        "cooldown": 0,
        "unique_in_sequence": False
    },
    "Nullptr":{
        "damage": 6,
        "pattern": [Vec2(1,0),Vec2(2,0)],
        "cooldown": 0,
        "unique_in_sequence": False
    },
    

    # "DashToDeadline": DashWeapon("DashToDeadline", 3, [Vec2(1,0)], 0,status_effects=[Status("Dizzy","brain")]),
    # "Exam": PatternWeapon("Exam", 10, [Vec2(1,0)], 0,status_effects=[Status("Anxiety","brain")]),
    # "Nullptr": PatternWeapon("Nullptr", 5, [Vec2(1,0),Vec2(2,0)], 0,unique_in_sequence=False,status_effects=[Status("Stress", "brain",stack=3)]),
}
weapon_registry = {

    "Hello World": PatternWeapon,
    "Pointer Sword": DashWeapon,
    "Template Greatsword": PatternWeapon,
    "Snake Roll": RollWeapon,
    "Exam":PatternWeapon,
    "Nullptr":PatternWeapon,
    "DashToDeadline":DashWeapon,
    "Goto Jump":MoveWeapon,
    "DragAndDrop":MoveWeapon,
    "DEBUG":MoveWeapon,
    "Data Mining":MineWeapon,
}