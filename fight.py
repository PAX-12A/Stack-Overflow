import pygame
import random
from font_manager import get_font
from colors import *
from Charactor import *

class FightScene:
    def __init__(self):
        # 游戏状态
        self.grid_size = BOARDSIZE + 1
        self.cell_width = 100
        self.cell_height = 80
        self.grid_start_x = (SCREEN_WIDTH - self.grid_size * self.cell_width) // 2
        self.grid_start_y = 300
        
        # 玩家和敌人
        self.player = Player()  # 开始在中间位置
        self.enemies = []
        self.spawn_enemy()
        
        # 游戏状态
        self.game_state = "player_turn"  # player_turn, enemy_turn, game_over
        self.turn_count = 0
        self.messages = []  # 队列，最新的消息插入末尾
        
        # 字体
        self.font = get_font("Cogmind",20)
        self.small_font = get_font("DOS",20)
        self.large_font = get_font("Cogmind",16)
        
        self.player.on_move_check = self.handle_move#回调函数绑定
        for enemy in self.enemies:
            enemy.on_move_check = self.handle_move


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

    
    def get_cell_rect(self, position):
        x = self.grid_start_x + position * self.cell_width
        y = self.grid_start_y
        return pygame.Rect(x, y, self.cell_width, self.cell_height)
    
    def get_cell_center(self, position):
        rect = self.get_cell_rect(position)
        return rect.centerx, rect.centery
    
    def get_pawn_at(self, pos, pawn_type="enemy"):
        if pawn_type == "enemy":
            pawns = self.enemies
        elif pawn_type == "player":
            pawns = [self.player]
        elif pawn_type == "all":
            pawns = []
            if self.player:   # 玩家存在才加
                pawns.append(self.player)
            pawns.extend(self.enemies)
        else:
            pawns = []
        # 🔑 过滤掉 None
        pawns = [p for p in pawns if p is not None]

        return next((pawn for pawn in pawns if pawn.position == pos), None)
    
    def get_enemy_positions(self):
        """返回已排序的敌人位置"""
        return sorted(enemy.position for enemy in self.enemies if enemy.alive)
    
    def get_closest_pawn(self, source_position , max_range=None, direction=None, pawn_type="enemy"):
        """
        从整个 scene 中找最近的单位
        :return: 最近的 pawn 或 None
        """
        # 根据 pawn_type 确定候选列表
        if pawn_type == "enemy":
            candidates = self.enemies
        elif pawn_type == "player":
            candidates = [self.player]
        elif pawn_type == "all":
            candidates = [self.player] + self.enemies
        else:
            candidates = []

        if not candidates:
            return None

        # 按方向过滤
        if direction == 1:  # 右边
            candidates = [p for p in candidates if p.position > source_position]
        elif direction == -1:  # 左边
            candidates = [p for p in candidates if p.position < source_position]

        if not candidates:
            return None

        # 找最近
        closest = min(candidates, key=lambda p: abs(p.position - source_position))

        # 射程判定
        if max_range is not None and abs(closest.position - source_position) > max_range:
            return None

        return closest
    
    def can_see(self,pawn1,pawn2):
        # 视线判定：两者之间没有其他单位阻挡
        if pawn1.position == pawn2.position:
            return True
        start = min(pawn1.position, pawn2.position)
        end = max(pawn1.position, pawn2.position)
        for enemy in self.enemies:
            if enemy.position > start and enemy.position < end:
                return False
        return True


 
    def handle_move(self, actor, new_pos):
        enemy = self.get_pawn_at(new_pos,"enemy")

        if enemy:#面前为敌人
            # 只有玩家可以换位，且要检查冷却
            if isinstance(actor, Player) and actor.swap_cooldown == 0:
                # 执行换位
                enemy.position, actor.position = actor.position, enemy.position
                actor.swap_cooldown = 4  # 重置换位冷却
                return actor.position  # 玩家位置更新后返回新位置
            else:
                # 敌人不能换位，玩家换位冷却中也不能换位
                return None
        else:
            if actor.can_move_to(new_pos) and self.player.position!=new_pos:#防止怪物跑到玩家脸上
                return new_pos
            else:
                return None

    
    def handle_event(self,event):
        if self.game_state != "player_turn":
            return
        
        if event.type == pygame.KEYDOWN:
            # === 移动：A / ←（左），D / →（右） ===
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                if self.player.move(-1):
                    self.end_player_turn()
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                if self.player.move(1):
                    self.end_player_turn()
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.player.turn_around()
                self.end_player_turn()
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.end_player_turn()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                index = event.key - pygame.K_1
                success, msg = self.player.try_add_weapon_to_sequence(index,self)
                if success:
                    self.end_player_turn()
                self.add_message(msg) 
            elif event.key == pygame.K_SPACE:
                if self.player.action_sequence:
                    self.execute_actions(self.player)
                    self.end_player_turn()
                else:
                    self.add_message("Empty Sequence!")
    def print_executed_actions(self,executed_actions):
        """
        打印 executed_actions 列表内容，不换行，用 -> 分隔
        executed_actions: [(index, weapon), ...]
        """
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
            multiplier = actor.damage_multiplier
            actual_damage = int(weapon.damage * multiplier)
            # print(f"actual_damage:{actual_damage}")
            # --- 类型1: melee / ranged（固定 pattern 攻击） ---
            if weapon.weapon_type in ["melee", "meleeMove"]:
                if weapon.weapon_type == "meleeMove":
                    actor.move(1)
                self.attack_by_pattern(weapon,actual_damage,actor)

            # --- 类型2: dash_to_enemy ---
            elif weapon.weapon_type == "dash_to_enemy":
                self.use_dash_to_enemy(weapon,actual_damage,actor)

            # --- 类型3: shoot（攻击最近敌人） ---
            elif weapon.weapon_type == "ranged":
                self.shoot(weapon,actual_damage,actor)


            # --- 类型4: fireball（攻击最近敌人±1格） ---
            elif weapon.weapon_type == "fireball":
                closest_pawn = self.get_closest_pawn(actor.position, direction=actor.direction,pawn_type="all")
                if closest_pawn:
                    print(f"explosion_center:{closest_pawn.position}")
                    for offset in weapon.pattern:
                        position = closest_pawn.position + offset
                        pawn = self.get_pawn_at(position,pawn_type="all")
                        if pawn:
                            pawn.take_damage(actual_damage,scene=self)
                            actor.apply_weapon_effects(pawn, weapon)

            elif weapon.weapon_type == "roll":
                new_pos=self.get_roll_target()
                if new_pos is None:
                    self.add_message("No valid roll target!")
                    self.player.move(1)
                else:
                    for pos in range(self.player.position + 1,new_pos):
                        if self.get_pawn_at(pos,"enemy"):
                            self.get_pawn_at(pos,"enemy").take_damage(actual_damage,scene=self)
                    self.player.position=new_pos

            pygame.display.flip()
            # pygame.time.wait(500) # 暂停0.5秒
            
            # print(666)


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




    def attack_by_pattern(self,weapon,actual_damage,actor):

        attack_positions = self.get_adjusted_attack_positions(weapon,actor)
        for enemy in self.enemies[:]:
            if enemy.position in attack_positions:
                enemy.take_damage(actual_damage,scene=self)
                actor.apply_weapon_effects(enemy, weapon)
        if self.player.position in attack_positions:
            self.player.take_damage(actual_damage,scene=self)
            actor.apply_weapon_effects(self.player, weapon)


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
        

    def use_dash_to_enemy(self, weapon,actual_damage,actor):
        # 获取当前方向最近的敌人
        closest_enemy = self.get_closest_pawn(actor.position, direction=actor.direction,pawn_type="all")
        
        if not closest_enemy:
            self.add_message(f"{weapon.name} No enemy")
            actor.position = self.get_legal_position(actor.position + actor.direction * weapon.range)
            return False

        distance = abs(closest_enemy.position - self.player.position)

        # 超出冲锋最大距离
        if distance > weapon.range:
            self.add_message(f"{weapon.name} Too far(Max {weapon.range} tile)")
            return False
        
        # 停在敌人前一格
        if actor.direction == 1:
            actor.position = closest_enemy.position - 1
        else:
            actor.position = closest_enemy.position + 1

        self.attack_by_pattern(weapon,actual_damage,actor)

        # 判断是否斩杀
        if closest_enemy.health <= 0:
            self.add_message("Kill!")
            # 冲到敌人所在格
            actor.position = closest_enemy.position

        return True

    def get_legal_position(self, postion):
        return max(0, min(self.grid_size - 1, postion))

    def get_adjusted_attack_positions(self, weapon, actor):
        adjusted_positions = []
        for offset in weapon.pattern:
            actual_offset = offset * actor.direction  # 左右翻转
            target_pos = actor.position + actual_offset
            if 0 <= target_pos < self.grid_size:
                adjusted_positions.append(target_pos)
        print(f"方向: {actor.direction}, 攻击格子: {adjusted_positions}")
        return adjusted_positions
    
    def get_occupied_positions(self):
        return {enemy.position for enemy in self.enemies}

    def spawn_enemy(self):
        # 获取所有未被占据的位置
        occupied_positions = {enemy.position for enemy in self.enemies}
        occupied_positions.add(self.player.position)

        possible_positions = [i for i in range(self.grid_size) if i not in occupied_positions]
        if not possible_positions:
            return  # 没有空位就不刷怪

        new_pos = random.choice(possible_positions)
        new_enemy = self.spawn_random_enemy(new_pos)
        new_enemy.on_move_check = self.handle_move
        self.enemies.append(new_enemy)
        # self.add_message("Enemy Arrived!")

    def spawn_random_enemy(self , position, monster_id=None):
        """从图纸库中生成敌人。"""
        if monster_id is None:
            monster_id = random.choice(list(MONSTER_LIBRARY.keys()))

        print(f"Spawned Monster: {monster_id}")
        data = MONSTER_LIBRARY[monster_id]
        
        enemy = Enemy(monster_id,position)
        enemy.name = data["name"]
        enemy.health = data["health"]
        enemy.sequence_limit = data["sequence_limit"]
        
        # 绑定武器（假设你已有 WEAPON_LIBRARY）
        enemy.weapons = [WEAPON_LIBRARY[w] for w in data["weapons"]]
        
        # 固定意图
        enemy.intents = data["intents"]
        
        return enemy

    
    def end_player_turn(self):
        if not self.enemies and self.turn_count>=50:
            self.game_state = "game_over"
            self.add_message("胜利!", 300)
            return        
        
        self.player.update_cooldowns()
        if self.player.swap_cooldown > 0:
            self.player.swap_cooldown -= 1
        if self.game_state != "game_over":
            self.game_state = "enemy_turn"
        self.turn_count += 1

        self.player.update_statuses()#更新状态
        
        # 每10回合刷2个敌人
        if self.turn_count % 10 == 0:
            self.spawn_enemy()
            self.spawn_enemy()
        
        # 执行敌人回合
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 1秒后执行敌人回合

    def end_enemy_turn(self):
        for enemy in self.enemies :      
            enemy.update_cooldowns()
        if self.game_state != "game_over":
            self.game_state = "player_turn"
                
        # 执行敌人回合
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 0.1秒后执行玩家回合
    
    def execute_enemy_turn(self,scene):
        for enemy in self.enemies:
            enemy.ai_take_turn(scene)
            self.end_enemy_turn()
        
        # 设置新的攻击意图
        if self.game_state != "game_over":
            self.game_state = "player_turn"
    
    def draw_grid(self,screen):
        for i in range(self.grid_size):
            rect = self.get_cell_rect(i)
            
            # 绘制网格背景
            color = BLACK
            # if i == self.player.position:
            #     color = GRAY  # 玩家位置
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 2)
            
            # 绘制位置编号
            pos_text = self.small_font.render(str(i), True, GRAY)
            text_rect = pos_text.get_rect(topleft=(rect.x + 5, rect.y + 5))
            screen.blit(pos_text, text_rect)
    
    def draw_entities(self,screen):
        self.draw_pawns(screen, self.player)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy_center = self.get_cell_center(enemy.position)
            
            # 绘制敌人血量
            health_ratio = enemy.health / enemy.max_health
            health_width = 40
            health_x = enemy_center[0] - health_width // 2
            health_y = enemy_center[1] - 35
            
            pygame.draw.rect(screen,SHADOW, (health_x, health_y, health_width, 6))
            pygame.draw.rect(screen, WHITE, (health_x, health_y, int(health_width * health_ratio), 6))

            self.draw_pawns(screen, enemy)

    def draw_pawns(self, screen , pawn):
        arrow_font = get_font("DOS", 24)
        character = pawn.get_sprite()

        if isinstance(pawn, Enemy) and pawn.state.__class__.__name__ == "MoveState":
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

        # 获取格子矩形 & 中心
        rect = self.get_cell_rect(pawn.position)
        center_x, center_y = rect.center

        # 角色图片居中
        draw_x = center_x - draw_img.get_width() // 2
        draw_y = center_y - draw_img.get_height() // 2
        screen.blit(draw_img, (draw_x, draw_y))

        # 箭头居中
        arrow_x = center_x - arrow_surface.get_width() // 2
        arrow_y = center_y + 15  
        screen.blit(arrow_surface, (arrow_x, arrow_y))

        if isinstance(pawn, Player):
            self.draw_hero_overlay(screen, pawn,(draw_x, draw_y + 50))
        elif isinstance(pawn, Enemy):
            self.draw_enemy_overlay(screen, pawn,(draw_x+20, draw_y))

    def draw_hero_overlay(self, screen, pawn: Player,pos):
        line = "*" * pawn.swap_cooldown
        cooldown_surface = self.font.render(line, True, GRAY)
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
            rect = weapon_image.get_rect(topleft=(intent_x - 24, intent_y))
            render_1bit_sprite(screen, weapon_image, rect.topleft, weapon_color)
            font = get_font("DOS", 16)
            screen.blit(font.render(f"{weapon.damage}", True, WHITE), (intent_x - 24, intent_y + 30))

            # 如果鼠标悬停在这个图标上
            if rect.collidepoint(mouse_pos):
                hovered_weapon = weapon

            intent_y -= 48  # 间距调整

        # # 加号（正在添加新动作）666
        # if pawn.adding:
        #     plus_surface = self.font.render("+", True, RED)
        #     screen.blit(plus_surface, (intent_x, intent_y))
        #     intent_y -= 48

        # # 状态标记
        # line = ""
        # if pawn.waiting:
        #     line += "!"
        # if pawn.ready_to_attack:
        #     line += "!!!"

        # if line:
        #     text_surface = self.small_font.render(line, True, weapon_color)
        #     screen.blit(text_surface, (intent_x-10, intent_y + 20))

        for symbol in pawn.state.get_intent_symbols(pawn):
            text_surface = self.small_font.render(
                symbol, True, weapon_color   # 👈 颜色仍由 UI 控制
            )
            screen.blit(text_surface, (intent_x, intent_y))
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
                font = get_font("en", "Patriot", 24)
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
        
        # 绘制武器状态
        weapon_y = 10
        for i, weapon in enumerate(self.player.weapons):
            color = GREEN if weapon.is_ready() else RED
            cooldown_text = f"{weapon.damage},{weapon.current_cooldown}" if not weapon.is_ready() else f"{weapon.damage},Ready"
            
            weapon_text = self.small_font.render(f"{i+1}.    {weapon.name} ({cooldown_text})", True, color)
            screen.blit(weapon_text, (10, weapon_y + i * 30))
            weapon_image = load_image(f"arts/sprite/weapons/{weapon.name}.png", (32, 32))
            render_1bit_sprite(screen, weapon_image, (30, weapon_y + i * 30 - 10 ), color)
        
        # 绘制动作序列
        if self.player.action_sequence:
            seq_text = self.font.render("Sequence:", True, WHITE)
            screen.blit(seq_text, (20, 400))
            
            for i, index in enumerate(self.player.action_sequence):
                weapon_name = self.player.weapons[index].name
                action_text = self.small_font.render(f"- {weapon_name}", True, GREEN)
                screen.blit(action_text, (30, 430 + i * 25))
        
    def draw_messages(self, screen, font, pos=(SCREEN_WIDTH-500, 400)):
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
    
    def draw(self, screen):
        # 绘制网格
        self.draw_grid(screen)
        
        # 绘制实体
        self.draw_entities(screen)
        
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
        
        if not self.enemies:
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
        self.player = Player(2)
        self.enemies = [Enemy(4)]
        self.game_state = "player_turn"
        self.turn_count = 0
        self.message = []


