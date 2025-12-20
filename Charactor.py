import pygame
import random
from font_manager import get_font
from colors import *
from Weapon import Weapon,weapon_info
from events import DeathEvent

class Status:
    def __init__(self, name, body_part, duration= 5,is_temp=True, is_illness=False, stack=1, unique=True):
        self.name = name                  # 状态名称，例如 "中毒"、"骨折"
        self.body_part = body_part        # 作用部位，例如 "brain"、"wholebody"、"left_arm"
        self.is_temp = is_temp            # 是否临时（True = 怪物施加/短期状态）
        self.duration = duration          # 持续回合数（None 代表永久）
        self.stack = stack                # 层数，叠加代表强度
        self.unique = unique              # 是否唯一（同名不可重复）
        self.is_illness = is_illness      # 是否疾病
        
    
    def update(self, owner):
        """每回合更新，返回 True 表示状态消失"""
        # if self.is_illness:
        #     return False  # 疾病不会自然消失
        
        # Stress 特殊处理
        if self.name == "Stress" and self.stack >= 3:
            illness = self.convert(owner)
            if illness:
                return True  # Stress 转化后消失
        
        # 常规持续时间逻辑
        if self.duration is not None:
            self.duration -= 1
            if self.duration <= 0:
                self.stack -= 1
                if self.stack <= 0:
                    return True
                else:
                    self.duration = self.reset_duration()
        return False


    def __repr__(self):
        if self.duration is None:
            return f"<Status {self.name} ({self.magnitude}) PERMANENT>"
        return f"<Status {self.name} ({self.stack}), {self.duration} turns>"
    
    def copy(self):
        """创建一个新的独立副本"""
        return Status(
            self.name,
            self.body_part,
            duration=self.duration,
            is_illness=self.is_illness,
            stack=self.stack, 
            unique=self.unique, 
            is_temp=self.is_temp
        )
    
    def reset_duration(self):
        """每层的独立持续时间，可以自定义"""
        return 50 if self.is_illness else 5 # 例如每层 Stress 默认 5 回合
    
    def convert(status, owner):
        """将 Stress 转化为疾病"""
        if status.name != "Stress":
            return None  # 只处理 Stress
        
        body_part = status.body_part
        diseases = DISEASE_CONVERSION_TABLE.get(body_part, [])
        if not diseases:
            return None  # 没有对应疾病
        
        # 转化概率：随着 stacks 增加而提高
        chance = min(0.2 * (status.stack - 2), 0.9)  
        # 例: 3层=20%，4层=40%，5层=60%，上限90%
        
        if random.random() < chance:
            new_disease_name = random.choice(diseases)
            illness = Status(new_disease_name, body_part, is_illness=True,duration=50)
            owner.add_status(illness)
            #print(f"[!] {owner} 的 {status.stack} 层压力转化为 {illness.name}")
            return illness
        
        return None
    
DISEASE_CONVERSION_TABLE = {
    "brain": ["Depression", "Insomnia", "Sleepy"],   # 抑郁、失眠、焦虑
    "stomach": ["Gastritis", "Ulcer"],                # 胃炎、胃溃疡
    "heart": ["Hypertension", "Arrhythmia"],          # 高血压、心律不齐
    "wholebody": ["Diabetes", "Chronic Fatigue"],     # 糖尿病、慢性疲劳
}

class Actor:
    def __init__(self, position=0, health=100, sequence_limit=2):
        self.position = position
        self.direction = 1
        self.health = health
        self.max_health = health
        self.action_sequence = []
        self.sequence_limit = sequence_limit
        self.sequence_length = 0
        self.damage_multiplier = 1.0
        self.status = []
        self.weapons = []
        self.battle_style = "queue"  # 或 stack
        self.on_move_check = None  # 回调（检测位置交换等）
        self.alive = True   # 是否存活

    def add_status(self, new_status):
        """添加状态：如果 unique 且已有同名，就覆盖"""
        if new_status.unique:
            for s in self.status:
                if s.name == new_status.name:
                    s.duration = new_status.duration+s.duration
                    s.stack = new_status.stack+s.stack
                    return
        self.status.append(new_status)
        print("Added status:", new_status)

    def apply_weapon_effects(self, target, weapon):
        """应用武器的附加状态"""
        for status in weapon.status_effects:
            target.add_status(status.copy())

    def remove_status(self, status_name):
        self.status = [s for s in self.status if s.name != status_name]

    def update_statuses(self):
        """每回合更新所有状态"""
        self.status = [s for s in self.status if not s.update(self)]

    def get_status_by_part(self, part):
        """获取某个部位的所有状态"""
        return [s for s in self.status if s.body_part == part]
    
    def take_damage(self, damage, scene):
        self.health -= damage

        self.add_status(Status("Simplified", "brain", is_illness=True))

        if self.health <= 0:
            scene.events.push(DeathEvent(self))

        # self.add_status(Status("PC addict", "brain", is_illness=True))
        # self.add_status(Status("Diabetes", "wholebody", is_illness=True))

    def die(self):
        """角色死亡的基础逻辑"""
        self.health = 0  # 确保血量为 0
        self.alive = False

    def remove_from_scene(self, scene):
        """从场景中移除角色"""
        if isinstance(self, Player):
            print(f"Removing player from the scene...")
        elif isinstance(self, Enemy):
            scene.enemies.remove(self)  # 移除敌人
        else:
            print(f"Unknown actor type: {self.name}")
    
    def update_cooldowns(self):
        for weapon in self.weapons:
            weapon.update_cooldown()

    def try_add_weapon_to_sequence(self, index, scene):
        if index < len(self.weapons):
            weapon = self.weapons[index]
            if weapon.unique_in_sequence and any(action == index for action in self.action_sequence):
                return False, f"{weapon.name} Already in Sequence!"
            if self.sequence_length >= self.sequence_limit:
                return False, "Reached Max Sequence Length!"
            elif self.weapons[index].is_ready():
                self.action_sequence.append(index)
                self.sequence_length += 1
                return True, f"{weapon.name} Added"
            else:
                return False, f"{weapon.name} Cooling!"
        return False, "无效的武器编号"
    
    def execute_sequence(self):
        executed_actions = []
        for index in self.action_sequence:
            weapon = self.weapons[index]
            if weapon.use():
                executed_actions.append((index, weapon))
        self.action_sequence.clear()
        self.sequence_length = 0
        return executed_actions
    
    def can_move_to(self, new_pos):
        return 0 <= new_pos <= BOARDSIZE
    
    def turn_around(self):
        self.direction *= -1
    
    def move(self, offset):
        new_pos = self.position + offset

        # === 让外部来决定能否移动（以及是否交换位置） ===
        if self.on_move_check:
            new_pos = self.on_move_check(self, new_pos)

        if new_pos is not None:
            self.position = new_pos
            return True
        # else:
        #     print("不能移动到该位置")
        return False
    
    def move_forward(self):
        return self.move(self.direction)
    
    def get_sprite(self):
        raise NotImplementedError

class Player(Actor):
    def __init__(self, position=2):
        super().__init__(position, health=50, sequence_limit=2)
        self.weapons = []
        self.skill_points = {
            "tech": 20,
            "lang": 5,
            "algo": 0,
            "skill":5,
        }
        self.swap_cooldown = 0  # 记录换位剩余冷却回合数
        self.available_skills = set(["Greenhand","DDL fever"])  # 可见技能
        self.learned_skills = set(["Student"])
        self.skill_effects = {}  # 技能效果字典
        attribute_names = {
        'S': 'Strength',     #- your overall health condition(physical defence/immune disease)
        'I': 'Intelligence', #- your programming ability (atk damage up,but prone to bugs、stress)
        'M': 'Mindset',      #- your mental health (psy defence/immune mental stress)
        'P': 'Perception',   #- gain more detailed info about yourself/enemy 、crital hit chance
        'L': 'Logic',        #- sequence limit、sequence bonus、adjustment cost
        'E': 'Earning',      #- 次要属性
        }
        self.base_stats = {k: 10 for k in ['S', 'I', 'M', 'P', 'L', 'E']}

        self.unlock_weapon("Hello World")  # 初始武器
        self.enabled_damage_decorators: set[str] = set() # 启用的伤害装饰器名称集合

    def die(self):
        """玩家死亡时的特殊逻辑"""
        super().die()  # 调用父类的 die() 处理基本死亡逻辑
        #self.game_state = "game_over"   # ✅ 切换游戏状态，而不是删掉 player

    def game_over(self):
        """游戏结束的逻辑"""
        print("Ending the game...")


    def unlock_weapon(self, weapon_name):
        if weapon_name not in self.weapons:
            if weapon_name in weapon_info:
                w = weapon_info[weapon_name]
                new_weapon = Weapon(
                    weapon_name,
                    w["damage"],
                    w["pattern"],
                    w["cooldown"],
                    w["color"],
                    weapon_type=w["weapon_type"],
                    unique_in_sequence=w["unique_in_sequence"],
                    range=w.get("range", None)
                )
                self.weapons.append(new_weapon)
                print(f"已解锁武器：{weapon_name}")
            else:
                print(f"武器名 {weapon_name} 不存在于weapon字典中。")

    def unlock_skill(self, skill_name: str):
        """解锁技能，并立即应用其效果"""
        if skill_name in self.learned_skills:
            return False  # 已解锁，跳过

        self.learned_skills.add(skill_name)
        self.available_skills.remove(skill_name)

        # 应用技能效果
        effect = SkillLibrary.get(skill_name)
        if effect:
            effect.apply(self)  
            self.skill_effects[skill_name] = effect
            print(f"[Skill] 解锁技能 {skill_name}，效果已生效。")
        else:
            print(f"[Skill] {skill_name} 未在技能库中定义。")
        return True
    
    def get_sprite(self):
        return load_image("arts/sprite/Character/hero.png")
    
class MonsterBlueprint:
    def __init__(self, id):
        data= MONSTER_LIBRARY[id]
        self.name = data["name"]
        self.health = data["health"]
        self.weapon_ids = data["weapons"]
        self.intents = data["intents"]
        self.type = data["type"]

    def create_weapons(self):
        return [WEAPON_LIBRARY[w] for w in self.weapon_ids]

class Enemy(Actor):
    def __init__(self,blueprint,position=5):
        # monster_data = MONSTER_LIBRARY[monster_id]
        super().__init__(position, 
                         health=blueprint.health, 
                         sequence_limit=3)

        self.name = blueprint.name
        self.type = blueprint.type

        # 根据怪物表装载武器
        self.weapons = blueprint.create_weapons()

        # 怪物的固定意图（技能组合）
        self.intents = blueprint.intents        # 出招表（静态）
        self.intent_index = 0           # 当前执行到第几个意图
        self.intent_progress = 0        # 当前意图中的武器进度

        # self.waiting = False  
        # self.ready_to_attack = False
        # self.adding = False
        # self.moving = False
        if self.type == "melee":
            self.strategy = MeleeMoveStrategy()
        else:
            self.strategy = RangedMoveStrategy()
        self.state = AddWeaponState()  # 初始状态
        

    def die(self):
        """敌人死亡时的特殊逻辑"""
        super().die()  # 调用父类的 die() 处理基本死亡逻辑
        print(f"Enemy dropped loot!")  # 显示敌人掉落物品提示
        # 这里可以增加掉落物品的逻辑

    def get_sprite(self):
        try:
            return load_image(f"arts/sprite/Character/{self.name}.png",(48,48)) 
        except FileNotFoundError:
            print("using default enemy img")
            return load_image("arts/sprite/Character/enemy.png")

    def execute_intent(self, scene):
        """逐回合执行当前意图"""
        if not self.intents:
            return

        current_intent = self.intents[self.intent_index]

        # 还没放完 → 本回合放一个
        if self.intent_progress < len(current_intent):
            weapon_name = current_intent[self.intent_progress]
            weapon_index = self.get_weapon_index(weapon_name)

            if weapon_index is not None:
                success, msg = self.try_add_weapon_to_sequence(weapon_index, scene)
                print(msg)
                if success:
                    self.intent_progress += 1
                    self.adding = False
                    if self.intent_progress == len(current_intent) :
                        self.waiting = True

            return False

        # 当前意图完成 → 切换到下一个
        self.intent_progress = 0
        self.intent_index = (self.intent_index + 1) % len(self.intents)
        return True

    def get_weapon_index(self, weapon_name):
        for i, w in enumerate(self.weapons):
            if w.name == weapon_name:
                return i
        return None
    
    

# 回合 N：
#     执行 A（EXECUTE）
#     ❌ 不显示 B 的 intent

# 回合 N+1：
#     显示 B 的 intent（INTENT）
#     ❌ 不执行 B

# 回合 N+2：
#     执行 B（EXECUTE）

    def ai_take_turn(self, scene):

        self.state = self.state.update(self, scene)
        # player = scene.player

        # if self.waiting:  
        #     # --- 检查能否命中玩家 ---
        #     if self.can_hit_player(player, scene):
        #         # 可以命中 → 保持等待状态，下一回合会攻击
        #         scene.add_message(f"Enemy is ready to attack")
        #         # 等待结束后下回合执行攻击
        #         self.waiting = False  
        #         self.ready_to_attack=True
        #     else:
        #         # --- 不能命中，先调整方向 ---
        #         if not self.is_facing_player(player):
        #             self.turn_around()
        #             # scene.add_message(f"Enemy turn around")
        #         elif self.moving:#再试图移动（如果已经在之前展示了移动的意图）
        #             self.move(self.direction)
        #             self.moving = False
        #         else: #展示移动的意图
        #             self.moving = True 
        #     return
        # elif self.ready_to_attack :# 之前一回合展示即将攻击            
        #     scene.execute_actions(self)# 施放攻击
        #     self.ready_to_attack=False        
        # else:
        #     if self.adding:# 展示过即将添加武器的意图                
        #         # print(self.intents)
        #         self.execute_intent(scene)# 执行意图  
        #     else:
        #         self.adding = True
    
    def is_facing_player(self, player):
        return (self.direction == 1 and player.position > self.position) or \
            (self.direction == -1 and player.position < self.position)
    
    def can_hit_player(self, player, scene):#临时的方案
        """检查当前方向 & 攻击模式能否命中玩家"""
        if player:
            distance = abs(self.position - player.position)
            if self.is_facing_player(player):
                if self.type == "melee":
                    return distance <= 1
                elif self.type == "range":
                    if scene.can_see(self,player):
                        print(f"Weapon Range:{self.weapons[0].range}, :{self.weapons[self.action_sequence[0]].range}")
                        if self.weapons[self.action_sequence[0]].range!=None:
                            return distance <= self.weapons[self.action_sequence[0]].range
                        else :
                            return distance <= 1

        return False

class EnemyState:
    def update(self, enemy, scene):
        raise NotImplementedError
    
    def get_weapon_color(self, enemy):
        return RED
    
    def get_intent_symbols(self, enemy) -> list[str]:
        return []

from enum import Enum

class Phase(Enum):
    INTENT = 0
    EXECUTE = 1

class MoveStrategy:
    def execute(self, enemy, scene):
        raise NotImplementedError
    
    def needs_move(self, enemy, scene):
        player = scene.player
        optimal_range = 1
        distance = abs(enemy.position - player.position)
        return distance > optimal_range or not enemy.is_facing_player(scene.player)

class MeleeMoveStrategy(MoveStrategy):
    def update(self, enemy, scene):
        player = scene.player
        optimal_range = 1
        distance = abs(enemy.position - player.position)

        if not enemy.is_facing_player(player):
            enemy.turn_around()
            return False

        if distance > optimal_range:
            enemy.move_forward()
            return False

        return True


class RangedMoveStrategy(MoveStrategy):

    def needs_move(self, enemy, scene):
        return not enemy.is_facing_player(scene.player)
    def update(self, enemy, scene):
        player = scene.player
        optimal_range = 10
        distance = abs(enemy.position - player.position)
        if not enemy.is_facing_player(player):
            enemy.turn_around()
            return False

        if distance < optimal_range:
            return True
        else:
            enemy.move_forward()

        return False
    
class MoveState(EnemyState):
    def __init__(self, move_strategy= MeleeMoveStrategy()):
        self.phase = Phase.INTENT
        self.strategy = move_strategy
    def update(self, enemy, scene):
        if self.phase == Phase.INTENT:
            scene.add_message(f"{enemy.name} intends to move")
            self.phase = Phase.EXECUTE
            return self

        if not self.strategy.needs_move(enemy, scene):
            return AttackState()
        
        self.strategy.update(enemy, scene)

        self.phase = Phase.INTENT
        return self

class AddWeaponState(EnemyState):

    def __init__(self):
        self.phase = Phase.INTENT
    def update(self, enemy, scene):
        finished = enemy.execute_intent(scene)

        if finished:
            if enemy.strategy.needs_move(enemy, scene):
                return MoveState(enemy.strategy)
            else:
                return AttackState()

        if self.phase == Phase.INTENT:
            scene.add_message(f"{enemy.name} is preparing weapons")
            self.phase = Phase.EXECUTE
            return self

        self.phase = Phase.INTENT
        return self

        
    def get_intent_symbols(self, enemy):
        if self.phase == Phase.INTENT:
            return ["+"]
        return []

class AttackState(EnemyState):
    def __init__(self):
        self.phase = Phase.INTENT

    def update(self, enemy, scene):
        if self.phase == Phase.INTENT:
            scene.add_message(f"{enemy.name} is about to attack")
            self.phase = Phase.EXECUTE
            return self

        scene.execute_actions(enemy)
        return AddWeaponState()
    
    def get_intent_symbols(self, enemy):
        return ["!"]
    def get_weapon_color(self, enemy):
        if self.phase == Phase.EXECUTE:
            return GREEN   # 即将攻击
        return RED
    


class SkillEffect:
    """技能效果对象"""
    def __init__(self, name, apply_func):
        self.name = name
        self.apply_func = apply_func

    def apply(self, player):
        self.apply_func(player)

class SkillLibrary:
    """技能库：集中定义所有技能"""
    _skills = {}

    @classmethod
    def register(cls, name, apply_func):
        cls._skills[name] = SkillEffect(name, apply_func)

    @classmethod
    def get(cls, name):
        return cls._skills.get(name, None)
    
    def init_skills():
        SkillLibrary.register("toughness", lambda p: setattr(p, "max_health", p.max_health + 20))
        SkillLibrary.register("queue", lambda p: setattr(p, "sequence_limit", p.sequence_limit + 1))
        SkillLibrary.register("Greenhand", lambda p: setattr(p, "max_health", p.max_health + 20))
        SkillLibrary.register("Hello world", lambda p: setattr(p, "sequence_limit", p.sequence_limit + 1))
        SkillLibrary.register(
            "DDL fever",
            lambda p: p.enabled_damage_decorators.add("DDL_fever")
        )

MONSTER_LIBRARY = {
    "DDL":{
        "name": "DDL Fiend",
        "health": 11,
        "type": "range",
        "weapons": ["DashToDeadline", "Exam"],
        "intents": [
            ["DashToDeadline"],
            ["DashToDeadline", "Exam"]
        ]
    },
    "GPA" : {
        "name": "GPA Phantom",
        "health": 10,
        "type": "range",
        "weapons": ["GPA--"],
        "intents": [
            ["GPA--"],
        ]
    },
    "BUG":{
        "name": "BUG",
        "health": 5,
        "type": "range",
        "weapons": ["Stack Overflow", "Compile Error"],
        "intents": [
            ["Stack Overflow"],
            ["Compile Error"]
        ]
    },
    "BUG2":{
        "name": "BUG",
        "health": 15,
        "type": "melee",
        "weapons": ["Nullptr"],
        "intents": [
            ["Nullptr"]
        ]
    },
}

WEAPON_LIBRARY = {
    "Exam": Weapon("Exam", 10, [1], 0, RED, weapon_type="melee",status_effects=[Status("Anxiety","brain")]),
    "Nullptr": Weapon("Nullptr", 5, [1,2], 0, GREEN, weapon_type="melee",unique_in_sequence=False,status_effects=[Status("Stress", "brain",stack=3)]),
    "GPA--": Weapon("GPA--", 5, [1], 0, RED, weapon_type="ranged", range=9,status_effects=[Status("Stress", "brain")]),
    "DashToDeadline": Weapon("DashToDeadline", 3, [1], 0, RED, weapon_type="dash_to_enemy", range=5,status_effects=[Status("Dizzy","brain")]),
    "Stack Overflow": Weapon("Stack Overflow", 8, [-1,0,1], 0, GREEN, weapon_type="fireball", range=5,status_effects=[Status("Anger", "brain")]),
    "Compile Error": Weapon("Compile Error", 10, [1], 0, RED, weapon_type="ranged", range=9,status_effects=[Status("Anxiety","brain")]),
}
