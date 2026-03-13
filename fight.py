import pygame
import random
from font_manager import get_font
from colors import *
from Charactor import *
from Damage import *
from events import *
from animation import *
from vfxsystem import VFXSystem
from grid import *
from camera import Camera


class FightScene:
    def __init__(self):
        # 游戏状态
        # self.grid_size = BOARDSIZE + 1
        self.grid_start_x = 100
        self.grid_start_y = 100

        self.grid = Grid(16,16)
        self.generate_map()
             
        # 游戏状态
        self.game_state = "player_turn"  # player_turn, enemy_turn, game_over
        self.turn_count = 0
        self.messages = []  # 队列，最新的消息插入末尾

        self.events = EventQueue()
        self.actions = deque()
        self.current_action=None
        self.vfx = VFXSystem()

        # 玩家和敌人
        self.player = Player(self)  # 开始在中间位置
        self.enemies = []
        for i in range(3):
            self.spawn_enemy()
        self.curent_wave = 1 
        self.win=False   

        # 字体
        self.font = get_font("Cogmind",20)
        self.small_font = get_font("DOS",20)
        self.large_font = get_font("Cogmind",16)

        #sequence拖动处理
        self.dragging_index = None
        self.dragging_weapon = None
        
        self.player.on_move_check = self.handle_move    #回调函数绑定
        for enemy in self.enemies:
            enemy.on_move_check = self.handle_move

        self.tiles = [
            load_image("arts/sprite/tiles/tile0.png",(64,64)),
            load_image("arts/sprite/tiles/tile1.png",(64,64)),
            load_image("arts/sprite/tiles/tile2.png",(64,64)),
            load_image("arts/sprite/tiles/tile3.png",(64,64)),
            load_image("arts/sprite/tiles/tile4.png",(64,64)),
        ]
        self.map_width = 16
        self.map_height = 16

        self.camera = Camera(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            GRID_WIDTH,
            GRID_HEIGHT,
            CELL_WIDTH
        )


    def generate_map(self):

        self.map_data = []

        for y in range(GRID_HEIGHT):

            row = []

            for x in range(GRID_WIDTH):

                # 边缘生成墙
                if x == 0 or y == 0 or x == GRID_WIDTH-1 or y == GRID_HEIGHT-1:
                    tile = 1

                else:
                    r = random.random()

                    if r < 0.8:
                        tile = 0      # 空地
                        if r < 0.2:
                            tile = row[-1] if x > 1 else 0
                    else:
                        tile = 2     # 地板
                row.append(tile)

            self.map_data.append(row)
        self.map_data[GRID_HEIGHT-2][8]=3 #出口

    def get_tile(self,pos):
        return self.map_data[pos.y][pos.x]
    
    def draw_map(self, screen):

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):

                tile_id = self.map_data[y][x]
                tile = self.tiles[tile_id]

                world_x = x * CELL_WIDTH
                world_y = y * CELL_HEIGHT

                screen_pos = self.camera.apply((world_x, world_y))

                screen.blit(tile, screen_pos)

                if tile_id == 0 :
                    text = f"{x},{y}"
                    text_img = self.small_font.render(text, True, GRAY)
                    screen.blit(text_img, screen_pos)


    def get_player_data(self):
        return {
            "health": self.player.health,
            "max_health": self.player.max_health,
            "sequence_limit":self.player.sequence_limit,
            "damage_multiplier":self.player.damage_multiplier,
            "status":self.player.status,
            "point":self.player.skill_points,
            "available_skills":self.player.available_skills,
            "learned_skills":self.player.learned_skills,
            "base_stats":self.player.base_stats
        }

    def add_message(self, text, color=WHITE, duration=2000):
        self.messages.append({
            "text": text,
            "color": color,
            "time": pygame.time.get_ticks(),
            "duration": duration,
            "alpha": 255
        })

    
    def get_cell_rect(self,pos):

        x = self.grid_start_x + pos.x * CELL_WIDTH
        y = self.grid_start_y + pos.y * CELL_HEIGHT

        return pygame.Rect(x,y,CELL_WIDTH,CELL_HEIGHT)
    
    def get_cell_center(self, position):
        rect = self.get_cell_rect(position)
        return rect.centerx, rect.centery

    def get_pawn_at(self, pos, pawn_type="all"):

        # 检查玩家
        if pawn_type in ("all", "player"):
            if self.player and self.player.position.x == pos.x and self.player.position.y == pos.y:
                return self.player

        # 检查敌人
        if pawn_type in ("all", "enemy"):
            for enemy in self.enemies:
                if enemy.position.x == pos.x and enemy.position.y == pos.y:
                    return enemy

        return None
    
    def get_enemy_positions(self):
        """返回已排序的敌人位置"""
        return sorted(enemy.position for enemy in self.enemies if enemy.alive)
    
    # def get_closest_pawn(self, source_position , max_range=None, direction=None, pawn_type="enemy"):
    #     """
    #     从整个 scene 中找最近的单位
    #     :return: 最近的 pawn 或 None
    #     """
    #     # 根据 pawn_type 确定候选列表
    #     if pawn_type == "enemy":
    #         candidates = self.enemies
    #     elif pawn_type == "player":
    #         candidates = [self.player]
    #     elif pawn_type == "all":
    #         candidates = [self.player] + self.enemies
    #     else:
    #         candidates = []

    #     if not candidates:
    #         return None

    #     # 按方向过滤
    #     if direction == 1:  # 右边
    #         candidates = [p for p in candidates if p.position.x > source_position.x]
    #     elif direction == -1:  # 左边
    #         candidates = [p for p in candidates if p.position.x < source_position.x]

    #     if not candidates:
    #         return None

    #     # 找最近
    #     closest = min(candidates, key=lambda p: (abs(p.position-source_position)+abs(p.position-source_position)))

    #     # # 射程判定
    #     # if max_range is not None and abs(closest.position - source_position) > max_range:
    #     #     return None

    #     return closest
    
    def can_see(self,pawn1,pawn2):#666
        # 视线判定：两者之间没有其他单位阻挡
        # if pawn1.position == pawn2.position:
        #     return True
        # start = min(pawn1.position, pawn2.position)
        # end = max(pawn1.position, pawn2.position)
        # for enemy in self.enemies:
        #     if enemy.position > start and enemy.position < end:
        #         return False
        return True
    
    def can_spawn(self,pos):
        return self.is_standable(pos) and pos not in self.get_occupied_pos()
    
    def get_occupied_pos(self):

        result = []

        for enemy in self.enemies:
            result.append(enemy.position)

        result.append(self.player.position)

        return result

    def is_standable(self,pos):

        return (
            self.is_wall(pos + Vec2(0,1))   # 脚下有地
            and not self.is_wall(pos)       # 自己位置不是墙
        )

    def mdis(p1,p2):#曼哈顿距离
        return abs(p1.x-p2.x)+abs(p1.x-p2.x)

 
    # def handle_move(self, actor, new_pos):
    #     enemy = self.get_pawn_at(new_pos,"enemy")
    
    #     if enemy:#面前为敌人
    #         # 只有玩家可以换位，且要检查冷却
    #         if isinstance(actor, Player) and actor.swap_cooldown == 0:
    #             # 执行换位
    #             enemy.position, actor.position = actor.position, enemy.position
    #             actor.swap_cooldown = 4  # 重置换位冷却
    #             return actor.position  # 玩家位置更新后返回新位置
    #         else:
    #             # 敌人不能换位，玩家换位冷却中也不能换位
    #             return None
    #     elif actor.can_move_to(new_pos):
    #         if self.player.position == new_pos:#防止怪物跑到玩家脸上
    #             return None
    #         if self.is_wall(new_pos):
    #             return None
    #         return new_pos
    #     else:
    #         return None

    def handle_move(self, actor, new_pos):

        if self.is_wall(new_pos):
            return None

        if self.player.position.x == new_pos.x and self.player.position.y == new_pos.y: #怪物不能走到玩家位置
            return None

        enemy = self.get_pawn_at(new_pos,"enemy")
        print(enemy)
        for e in self.enemies:
            print(e.position)

        if enemy:

            if isinstance(actor, Player) and actor.swap_cooldown == 0:#玩家的换位技能

                old_actor = actor.position
                old_enemy = enemy.position

                # enemy.position = old_actor
                # enemy.move(Vec2(old_actor.x-old_enemy.x,0))
                # print(666666)
                    # ✅ 给敌人也播放移动动画
                enemy.position = old_actor
                enemy.anim.play(
                    MoveAnimation(enemy.idle_frames, enemy, old_enemy, old_actor)
                )

                actor.swap_cooldown = 4

                return old_enemy

            return None

        if actor.can_move_to(new_pos):
            return new_pos

        return None

    def is_wall(self,pos):
        tile=self.get_tile(pos)
        if(tile==3):#出口
            return False
        return tile

    
    def handle_event(self,event):
        if self.game_state != "player_turn":
            return
        
        if event.type == pygame.KEYDOWN:
            # === 移动：A / ←（左），D / →（右） ===
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                if self.player.move(Vec2(-1,0)):
                    self.end_player_turn()
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                if self.player.move(Vec2(1,0)):
                    self.end_player_turn()
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.player.move(Vec2(0,-1))            
                self.end_player_turn()
                self.player.move(Vec2(0,-1)) 
            elif event.key in [pygame.K_z]:
                self.player.turn_around()
                self.end_player_turn()
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.end_player_turn()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                index = event.key - pygame.K_1
                success, msg = self.player.try_add_weapon_to_sequence(index,self)
                if success:
                    self.end_player_turn()
                # self.add_message(msg) 
            elif event.key == pygame.K_SPACE:
                if self.player.action_sequence:
                    self.execute_actions(self.player)
                    self.end_player_turn()
                else:
                    self.add_message("Empty Sequence!")
        elif event.type == pygame.MOUSEBUTTONDOWN:#移动序列的内容
            mx, my = event.pos
            for i in range(len(self.player.weapons)):
                rect2 = self.get_weapon_rect(i)
                if rect2.collidepoint(mx, my):
                    success, msg = self.player.try_add_weapon_to_sequence(i,self)
                    if success:
                        self.end_player_turn()
                    self.add_message(msg) 
            for i, index in enumerate(self.player.action_sequence):
                # print(event.pos)
                rect = self.get_sequence_rect(i)
                if rect.collidepoint(mx, my):
                    self.dragging_index = i
                    self.dragging_weapon = index
                    print(self.dragging_index,self.dragging_weapon)
                    break



        elif event.type == pygame.MOUSEBUTTONUP:

            if self.dragging_weapon is not None:

                mx, my = event.pos

                new_index = None

                for i in range(len(self.player.action_sequence)):

                    rect = self.get_sequence_rect(i)

                    if rect.collidepoint(mx, my):
                        new_index = i
                        break

                if new_index is not None:

                    seq = self.player.action_sequence

                    weapon = seq.pop(self.dragging_index)
                    seq.insert(new_index, weapon)

                self.dragging_weapon = None
                self.dragging_index = None

    def print_executed_actions(self,executed_actions):
        if not executed_actions:
            print("No actions executed.")
            return

        for i, (index, weapon) in enumerate(executed_actions):
            end_char = "->" if i < len(executed_actions) - 1 else "\n"
            print(f"{weapon.name}({index})", end=end_char)


    def execute_actions(self,actor):
        executed_actions = actor.execute_sequence()

        if self.player.battle_style == "stack":# stack风格反转序列
            executed_actions.reverse()
        self.print_executed_actions(executed_actions)
        
        for weapon_index, weapon in executed_actions:
            # print("atk triggered")
            # === 1. 加算 / 基础阶段 ===
            base = int(weapon.damage * actor.damage_multiplier)
            damage = Damage(base)

            # === 2. Decorator 阶段（按规则包） ===
            if isinstance(actor, Player):
                # print(f"Player enabled decorators: {actor.enabled_damage_decorators}")
                if "DDL_fever" in actor.enabled_damage_decorators:
                    damage = DDLFeverDecorator(damage, actor)

            # 以后可以继续包：
            # damage = CriticalDecorator(damage)
            # damage = VulnerableDecorator(damage, target)
            # damage = ShieldDecorator(damage, target)

            # actual_damage = damage.value()

            self.actions.append(
                AttackAction(actor, weapon, damage)
            )
            self.finish_action()# may have a problem

    def get_roll_target(self):
            positions = self.get_enemy_positions()
            if not positions:
                return None

            if self.player.direction == 1:  # 朝右
                # 找到第一个比玩家位置大的连续区间
                group = []
                for p in positions:
                    if p > self.player.position:
                        if not group or p == group[-1] + 1:
                            group.append(p)
                        else:
                            break
                return group[-1] + 1 if group and group[-1] + 1<= BOARDSIZE else None

            elif self.player.direction == -1:  # 朝左
                # 找到第一个比玩家位置小的连续区间（从右往左扫）
                group = []
                for p in reversed(positions):
                    if p < self.player.position:
                        if not group or p == group[-1] - 1:
                            group.append(p)
                        else:
                            break
                return group[-1] - 1 if group and group[-1] + 1<= BOARDSIZE else None

            return None

    def attack_by_pattern(self, weapon, actual_damage, actor):

        attack_positions = self.get_adjusted_attack_positions(weapon, actor)
        actor.state_machine.change(AttackState(actor, attack_positions , actual_damage))

    def shoot(self, weapon,actual_damage,actor):
        # 获取当前方向最近的敌人
        closest_enemy = self.get_closest_pawn(actor.position, direction=actor.direction,pawn_type="all")
        
        if not closest_enemy:
            self.add_message(f"{weapon.name} No enemy")
            return False

        distance = abs(closest_enemy.position - actor.position)

        closest_enemy.take_damage(actual_damage,scene=self)
        actor.apply_weapon_effects(closest_enemy, weapon)

        # 超出最大射程
        if distance > weapon.range:
            self.add_message(f"{weapon.name} Too far(Max {weapon.range} tile)")
            return False
        
    def get_closestL_pawn(self,pos,direction):#看一行的最近敌人,用于dash
        # print(pos,direction)
        i = pos.x + direction
        while 0 < i < GRID_WIDTH - 1:
            if self.is_wall(Vec2(i,pos.y)): #遇到墙停止
               return None
            pawn = self.get_pawn_at(Vec2(i,pos.y))
            if pawn:
                return pawn
            i+=direction
        return None

    def use_dash_to_enemy(self, weapon, damage, actor):
        closest_enemy = self.get_closestL_pawn(actor.position, actor.direction)

        if not closest_enemy:
            actor.move(Vec2(1,0))
            self.add_message(f"{weapon.name} No enemy")
            self.finish_action()
            return False

        target_x = closest_enemy.position.x - actor.direction
        offset = Vec2(target_x - actor.position.x, 0)

        self.actions.appendleft(PatternAttackAction(actor, weapon, damage))  # 不会再路由回 dash
        self.actions.appendleft(MoveAction(actor, offset))
        self.finish_action()
        return True

    def get_legal_position(self, postion):
        return max(0, min(self.grid_size - 1, postion))

    def get_adjusted_attack_positions(self, weapon, actor):
        adjusted_positions = []
        for offset in weapon.pattern:
            actual_offset = offset * actor.direction  # 左右翻转
            target_pos = actor.position + actual_offset
            # if 0 <= target_pos.x < GRID_WIDTH & 0 <= target_pos.y < GRID_HEIGHT:
            adjusted_positions.append(target_pos)
        print(f"{actor.name}攻击方向: {actor.direction}, 攻击格子: {adjusted_positions}")
        return adjusted_positions
    
    def get_occupied_positions(self):
        return {enemy.position for enemy in self.enemies}
    
    def spawn_enemy(self):

        pos = self.get_random_spawn_pos()

        if pos is None:
            return

        enemy = self.create_random_enemy(pos)

        enemy.on_move_check = self.handle_move

        self.enemies.append(enemy)

    def get_random_spawn_pos(self):

        for i in range(20):

            x = random.randint(1, GRID_WIDTH-2)
            y = random.randint(1, GRID_HEIGHT-2)

            pos = Vec2(x,y)

            if self.can_spawn(pos):
                return pos

        return None

    def create_random_enemy(self , position, monster_id=None):
        """从图纸库中生成敌人。"""
        enemy = EnemyFactory.create(self,position)
        return enemy
    
    def end_player_turn(self):
        self.game_state = "enemy_turn"
        # print("turn end")
        if not self.is_standable(self.player.position):
            self.player.move(Vec2(0,1))#下坠1格

        if self.get_tile(self.player.position) == 3:
            self.game_state = "game_over"
            self.add_message("胜利!", 300)
            self.win=True
            return  

        if  self.curent_wave>4:
            self.game_state = "game_over"
            self.add_message("胜利!", 300)
            self.win=True
            return        
        

        self.player.update_cooldowns()
        if self.player.swap_cooldown > 0:
            self.player.swap_cooldown -= 1
        if self.game_state != "game_over":
            self.game_state = "enemy_turn"
        self.turn_count += 1

        self.player.update_statuses()#更新状态
        
        # # 每10回合刷2个敌人
        # if self.turn_count % 10 == 0:
        #     self.spawn_enemy()
        #     self.spawn_enemy()
        # if len(self.enemies) == 0 :
        #     # self.spawn_enemy()
        #     # self.spawn_enemy()
        #     # self.spawn_enemy()
        #     self.curent_wave += 1

        # if(self.actions):
        #     for act in self.actions:
        #         print(f"actions:{self.current_action},{act.actor.name},{act.weapon.name}")
        # print(self.player.position,self.is_standable(self.player.position))

        # 执行敌人回合
        # pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 0.1秒后执行敌人回合

    def end_enemy_turn(self):
        for enemy in self.enemies : 
            enemy.move(Vec2(0,1))#下坠1格     
            enemy.update_cooldowns()
        if self.game_state != "game_over":
            self.game_state = "player_turn"
                
        # # 执行敌人回合
        # pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 0.1秒后执行玩家回合
    
    def execute_enemy_turn(self,scene):
        for enemy in self.enemies:
            enemy.ai_take_turn(scene)
            self.end_enemy_turn()
        
        # 设置新的攻击意图
        if self.game_state != "game_over":
            self.game_state = "player_turn"
    
    def screen_reflection(self,pos):
        world_x = pos.x * CELL_WIDTH
        world_y = pos.y * CELL_HEIGHT

        return self.camera.apply((world_x, world_y))
    
    def draw_entities(self,screen):
        self.draw_pawns(screen, self.player)
        
        # 绘制敌人
        for enemy in self.enemies:
            #print(enemy.position)
            # enemy_center = self.get_cell_center(enemy.position)
            
            # 绘制敌人血量
            health_ratio = enemy.health / enemy.max_health
            health_width = 40

            screen_pos=self.screen_reflection(enemy.render_pos)
            health_x = screen_pos[0]
            health_y = screen_pos[1]
            # print(enemy_center,pygame.mouse.get_pos())
            pygame.draw.rect(screen,SHADOW, (health_x,health_y, health_width, 6))
            pygame.draw.rect(screen, WHITE, (health_x,health_y, int(health_width * health_ratio), 6))
            hp_text = self.small_font.render(str(enemy.health), True, GREEN)

            screen.blit(hp_text,(health_x,health_y))

            self.draw_pawns(screen, enemy)

    def draw_pawns(self, screen , pawn):
        arrow_font = get_font("DOS",24)
        character = pawn.anim.get_frame()

        if isinstance(pawn, Enemy) and (pawn.state.phase == Phase.EXECUTE and pawn.state.__class__.__name__ == "MoveState"):
            arrow_color = GREEN
        else:
            arrow_color = GRAY
            
        # 根据方向翻转
        if pawn.direction == 1:  # 朝右
            draw_img = character
            arrow_surface = arrow_font.render("->", True, arrow_color)
        else:  # 朝左
            draw_img = pygame.transform.flip(character, True, False)
            arrow_surface = arrow_font.render("<-", True, arrow_color)

        screen_pos=self.screen_reflection(pawn.render_pos)

        screen.blit(draw_img,screen_pos)

        # # 箭头居中
        # arrow_x = center_x - arrow_surface.get_width() // 2
        # arrow_y = center_y + 15  
        # screen.blit(arrow_surface, (arrow_x, arrow_y))

        if isinstance(pawn, Player):
            self.draw_hero_overlay(screen, pawn,screen_pos)
        elif isinstance(pawn, Enemy):
            self.draw_enemy_overlay(screen, pawn,screen_pos)

    def draw_hero_overlay(self, screen, pawn: Player,pos):
        line = "*" * pawn.swap_cooldown
        cooldown_surface = self.font.render(line, True, GREEN)
        screen.blit(cooldown_surface, pos)

    def draw_enemy_overlay(self, screen, pawn: Enemy,pos):
        self.draw_intents(screen, pawn, pos)

    def draw_intents(self, screen, pawn, pos):
        intent_x = pos[0] 
        intent_y = pos[1] - 90

        mouse_pos = pygame.mouse.get_pos()
        hovered_weapon = None  # 当前悬停的武器
        weapon_color = pawn.state.get_weapon_color(pawn)

        for index in pawn.action_sequence:
            weapon = pawn.weapons[index]
            weapon_image = load_image(f"arts/sprite/weapons/{weapon.name}.png",(48,48))

            # 绘制图标
            rect = weapon_image.get_rect(topleft=(intent_x, intent_y))
            render_1bit_sprite(screen, weapon_image, rect.topleft, weapon_color)
            font = get_font("DOS", 16)
            screen.blit(font.render(f"{weapon.damage}", True, WHITE), (intent_x , intent_y + 30))#左下角为伤害

            # 如果鼠标悬停在这个图标上
            if rect.collidepoint(mouse_pos):
                hovered_weapon = weapon

            intent_y -= 48  # 间距调整

        for symbol in pawn.state.get_intent_symbols(pawn):
            if symbol == "!":
                name = "Warning"
            elif symbol == "+":
                name = "Adding"
            symbol_image = load_image(f"arts/sprite/weapons/{name}.png", (48, 48))
            render_1bit_sprite(screen, symbol_image, (intent_x, intent_y), weapon_color)
            intent_y -= 48


        # ==============================
        # 悬停时绘制武器详细信息 Tooltip
        # ==============================
        if hovered_weapon:
            self.draw_weapon_tooltip(screen, hovered_weapon, mouse_pos)

    def draw_weapon_tooltip(self, screen, weapon, pos):
        
        """在鼠标位置显示武器信息"""
        lines = [
            f"{weapon.name}",
            f"Damage: {weapon.damage}",
            f"Range: {getattr(weapon, 'range', 'N/A')}",
            f"Type: {weapon.weapon_type}"
        ]

        padding = 5
        width = 200
        height = len(lines) * 18 + padding * 2

        x, y = pos
        rect = pygame.Rect(x + 15, y + 15, width, height)

        # 黑底
        pygame.draw.rect(screen, (0, 0, 0), rect)

        # 多层发光描边（外圈先画深色，内圈画亮色）
        pygame.draw.rect(screen,GREEN, rect, 1)               # 明亮红线


        # 文本
        for i, line in enumerate(lines):
            if i==0:
                font = get_font("Patriot", 24)
            else:
                font = self.small_font
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (rect.x + padding, rect.y + padding + i * 18))

    def draw_ui(self,screen):
        # 绘制玩家血量,假设最大血量是 10 格
        max_bar_length = 10  
        filled = int(self.player.health / self.player.max_health * max_bar_length)
        bar_str = "#" * filled + "." * (max_bar_length - filled)
        health_text = self.small_font.render(f"HP: {bar_str}({self.player.health}/{self.player.max_health})", True, WHITE)
        screen.blit(health_text, (30, SCREEN_HEIGHT-80))
        
        # 绘制回合数
        turn_text = self.font.render(f"Turn: {self.turn_count}", True, WHITE)
        screen.blit(turn_text, (SCREEN_WIDTH- 200, 20))

        wave_text = self.font.render(f"Wave: {self.curent_wave}/4", True, WHITE)
        screen.blit(wave_text, (SCREEN_WIDTH- 200, 70))
        
        # 绘制武器状态
        weapon_y = 10
        for i, weapon in enumerate(self.player.weapons):
            color = GREEN if weapon.is_ready() else RED
            cooldown_text = f"{weapon.damage},{weapon.current_cooldown}" if not weapon.is_ready() else f"{weapon.damage},Ready"
            
            weapon_text = self.small_font.render(f"{i+1}.     {weapon.name} ({cooldown_text})", True, color)
            screen.blit(weapon_text, (10, weapon_y + i * 40))
            weapon_image = load_image(f"arts/sprite/weapons/{weapon.name}.png", (32, 32))
            render_1bit_sprite(screen, weapon_image, (40, weapon_y + i * 40 - 10 ), color)
        
        # 绘制动作序列
        if self.player.action_sequence:
            seq_text = self.font.render("Sequence:", True, WHITE)
            screen.blit(seq_text, (20, 400))
            
            for i, index in enumerate(self.player.action_sequence):
                if i == self.dragging_index:#不画选中的
                    continue
                weapon_name = self.player.weapons[index].name
                # action_text = self.small_font.render(f"- {weapon_name}", True, GREEN)
                # screen.blit(action_text, (30, 430 + i * 25))
                weapon_image = load_image(f"arts/sprite/weapons/{weapon_name}.png",(48,48))
                rect = self.get_sequence_rect(i)
                render_1bit_sprite(screen, weapon_image, rect.topleft, GREEN)
                # print(f"INDEX:{self.dragging_weapon}")

                if self.dragging_weapon is not None:

                    weapon_name = self.player.weapons[self.dragging_weapon].name

                    weapon_image = load_image(
                        f"arts/sprite/weapons/{weapon_name}.png",
                        (48,48)
                    )

                    render_1bit_sprite(screen, weapon_image, (pygame.mouse.get_pos()), GREEN)

    def get_sequence_rect(self, i):
        return pygame.Rect(10 + i * 64, 430, 48, 48)
    
    def get_weapon_rect(self, i):
        return pygame.Rect(40, i * 40 - 10 , 48, 48)
        
    def draw_messages(self, screen, font, pos=(SCREEN_WIDTH-500, 500)):
        now = pygame.time.get_ticks()
        y_offset = 0
        to_remove = []

        for msg in self.messages:
            elapsed = now - msg["time"]

            # 进入淡出阶段
            if elapsed > msg["duration"]:
                fade_progress = min((elapsed - msg["duration"]) / 500, 1)
                msg["alpha"] = 255 * (1 - fade_progress)

            # 完全透明就删除
            if msg["alpha"] <= 0:
                to_remove.append(msg)
                continue

            # 渲染文字
            text_surface = font.render(msg["text"], True, msg["color"])
            text_surface.set_alpha(int(msg["alpha"]))
            screen.blit(text_surface, (pos[0], pos[1] + y_offset))

            y_offset += font.get_height() + 5  # 每条消息向下偏移

        # 清理过期消息
        for msg in to_remove:
            self.messages.remove(msg)    

    # def update(self):

    #     # 1. 如果是敌人回合且没有正在执行的动作和动画，才执行敌人逻辑
    #     if self.game_state == "enemy_turn":
    #         if not self.current_action and not self.actions:
    #             if self._enemy_turn_ready():        # ✅ 所有敌人动画都结束了
    #                 self.execute_enemy_turn(self)

    #     # print(self.actions)
    #     # if self.current_action :
    #     #     print(self.current_action.weapon)
    #     # self.current_action=None

    #     # 1. ActionQueue
    #     dt = 1/60

    #     if not self.current_action and self.actions:
    #         self.current_action = self.actions.popleft()
    #         self.start_action(self.current_action)

    #     # 2. StateMachine
    #     for enemy in self.enemies:
    #         enemy.state_machine.update(0.1)

    #     self.player.state_machine.update(0.1)

    #     # 3. EventQueue
    #     self.process_events()

    #     # 4. VFX
    #     self.vfx.update(0.1)

    #     # 5. Camera
    #     self.camera.update(self.player)

    #     self.player.anim.update(dt)
    #     for enemy in self.enemies:
    #         enemy.anim.update(dt)
# FightScene.update() 里加入回合驱动
    def update(self):
        print(self.actions)

        # 1. 如果是敌人回合且没有正在执行的动作和动画，才执行敌人逻辑
        if self.game_state == "enemy_turn":
            if not self.current_action and not self.actions:
                self._enemy_turn_ready()        # tmp
                self.execute_enemy_turn(self)

        # 2. ActionQueue
        if not self.current_action and self.actions:
            self.current_action = self.actions.popleft()
            self.start_action(self.current_action)

        # 统一 dt
        dt = 1/60
        for enemy in self.enemies:
            enemy.state_machine.update(dt)     # 统一用同一个 dt
        self.player.state_machine.update(dt)

        self.process_events()
        self.vfx.update(dt)
        self.camera.update(self.player)

        self.player.anim.update(dt)
        for enemy in self.enemies:
            enemy.anim.update(dt)

    def _enemy_turn_ready(self):
        """所有敌人的动画都播完了才返回 True"""
        for enemy in self.enemies:
            #print(enemy.anim.current.index)
            if enemy.anim.current is not None:
                return False
        return True

    def start_action(self, action):#666
        if isinstance(action, MoveAction):
            actor = action.actor
            actor.move(action.offset)       # move 触发 MoveState
            # MoveState 结束时调用 finish_action，队列自动推进到下一个 AttackAction
            return
        if isinstance(action, PatternAttackAction):         # ✅ 直接走 pattern
            self.attack_by_pattern(action.weapon, action.damage, action.actor)
            return
        if isinstance(action, AttackAction):
            actor = action.actor
            weapon = action.weapon
            damage = action.damage
            actual_damage = damage.value()

            # --- 类型1: melee / ranged（固定 pattern 攻击） ---
            if weapon.weapon_type in ["melee", "meleeMove"]:
                if weapon.weapon_type == "meleeMove":actor.move(1)
                self.attack_by_pattern(weapon,actual_damage,actor)

            # --- 类型2: dash_to_enemy ---
            elif weapon.weapon_type == "dash_to_enemy":
                self.use_dash_to_enemy(weapon,actual_damage,actor)

            # # --- 类型3: shoot（攻击最近敌人） ---
            # elif weapon.weapon_type == "ranged":
            #     self.shoot(weapon,actual_damage,actor)
            #     self.finish_action() #tmp

            # # --- 类型4: fireball（攻击最近敌人±1格） ---
            # elif weapon.weapon_type == "fireball":
            #     closest_pawn = self.get_closest_pawn(actor.position, direction=actor.direction,pawn_type="all")
            #     if closest_pawn:
            #         print(f"explosion_center:{closest_pawn.position}")
            #         for offset in weapon.pattern:
            #             position = closest_pawn.position + offset
            #             pawn = self.get_pawn_at(position,pawn_type="all")
            #             if pawn:
            #                 self.events.push(DamageEvent(actor, pawn, actual_damage)) #入队
            #                 actor.apply_weapon_effects(pawn, weapon)
            #     self.finish_action() #tmp

            # elif weapon.weapon_type == "roll":
            #     new_pos=self.get_roll_target()
            #     if new_pos is None:
            #         self.add_message("No valid roll target!")
            #         self.player.move(1)
            #     else:
            #         actor.state_machine.change(AttackState(actor, range(min(self.player.position + 1, new_pos), max(self.player.position + 1, new_pos)) , actual_damage))
            #         self.player.position=new_pos


    def finish_action(self):
        self.current_action = None
        # pygame.time.wait(300)

    def draw(self, screen):
        
        self.draw_map(screen)
        
        # 绘制实体
        self.draw_entities(screen)

        self.vfx.draw(screen)
        
        # 绘制UI
        self.draw_ui(screen)
        
        # 绘制消息
        self.draw_messages(screen,self.small_font)

        # 游戏结束屏幕
        if self.game_state == "game_over":
            self.game_over(screen)


    def game_over(self,screen):
        # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # overlay.set_alpha(128)
        # overlay.fill(WHITE)
        # screen.blit(overlay, (0, 0))
        screen.fill(BLACK)
        
        if self.win:
            end_text = self.large_font.render("Congratulations!", True, GREEN)
        else:
            end_text = self.font.render("You Failed!", True, RED)
            render_ascii_art(screen, label="grave",x=100, y=200, font_size=24, color=WHITE)
            character = load_image('arts/grave.png')
            screen.blit(character, (800, 50))
        
        end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2+200))
        screen.blit(end_text, end_rect)
        
        restart_text = self.font.render("Q to return Menu,R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 220))
        screen.blit(restart_text, restart_rect)    
    
    def restart_game(self):
        self.player = Player(self)
        self.enemies = [Enemy(self,4)]
        self.game_state = "player_turn"
        self.turn_count = 0
        self.message = []

    def process_events(self):
        while not self.events.empty():
            event = self.events.pop()
            self.handle_scene_event(event)

    def handle_scene_event(self, event):

        if isinstance(event, DamageEvent):
            if(event.target == None):
                return
            event.target.health -= event.amount
            print(f"{event.target.name} took {event.amount} damage, health now {event.target.health}")

            if event.target.health <= 0:
                self.events.push(DeathEvent(event.target))

        elif isinstance(event, DeathEvent):
            pawn = event.pawn
            pawn.die()

            if isinstance(pawn, Enemy):
                if pawn in self.enemies:
                    self.enemies.remove(pawn)
                self.events.push(MessageEvent("Enemy Defeated!", GREEN))

            elif isinstance(pawn, Player):
                self.game_state = "game_over"

        elif isinstance(event, MessageEvent):
            self.add_message(event.text, event.color)





