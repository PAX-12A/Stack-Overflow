from colors import *

class Tab:
    def __init__(self, name, x, y):
        self.name = name
        self.rect = pygame.Rect(x, y, TAB_WIDTH, TAB_HEIGHT)
        self.is_active = False
        self.is_hovered = False
        
    def draw(self, screen, font,img=True):
        # 选择颜色
        if self.is_active:
            color = WHITE
            text_color = BLACK
        elif self.is_hovered:
            color = GRAY
            text_color = WHITE
        else:
            color = BLACK
            text_color = WHITE
            
        # 绘制标签背景（带边框效果）
        pygame.draw.rect(screen, SHADOW, (self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # 绘制文字
        text_surface = font.render(self.name, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        if img:
            render_1bit_sprite(screen, load_image(f"arts/sprite/{self.name}.png",(48,48)), (self.rect.x-3, self.rect.y-3), text_color)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Page:
    def __init__(self, name):
        self.name = name
        self.is_active = False

    def handle_event(self, event, player):
        """处理用户输入"""
        return False

    def update(self, player):
        """更新页面逻辑"""
        pass

    def draw(self, screen, font, player):
        """绘制页面内容"""
        pass

class PageContainer(Page):
    def __init__(self, name, get_player_data, tab_pos, direction="row"):
        super().__init__(name)
        self.tabs = []
        self.pages = {}
        self.active_page = None
        self.get_player_data = get_player_data
        self.tab_pos = tab_pos
        self.direction = direction

    def register_page(self, page):
        x, y = self.tab_pos
        if self.direction == "row":
            tab_x = x + len(self.tabs) * (TAB_WIDTH + 10)
            tab_y = y
        else:
            tab_x = x
            tab_y = y + len(self.tabs) * (TAB_HEIGHT + 10)

        tab = Tab(page.name, tab_x, tab_y)
        self.tabs.append(tab)
        self.pages[page.name] = page

    def handle_event(self, event, player):
        # Tab 切换
        for tab in self.tabs:
            if tab.handle_event(event):
                if tab.is_active:
                    tab.is_active = False
                    self.active_page = None
                else:
                    for t in self.tabs:
                        t.is_active = False
                    tab.is_active = True
                    self.active_page = self.pages[tab.name]
                return True

        # 把事件交给子页面
        if self.active_page:
            return self.active_page.handle_event(event, player)

    def update(self, player):
        if self.active_page:
            self.active_page.update(player)

    def draw(self, screen, font, player):
        # 绘制 Tabs
        icon_font = get_font("Cogmind", 20)
        for tab in self.tabs:
            tab.draw(screen, icon_font)
        # 绘制子页面
        if self.active_page:
            self.active_page.draw(screen, font, player)

class InventoryPage(Page):
    def __init__(self):
        super().__init__("Inventory")

    def draw(self, screen, font, player=None):
        lines = [
            "这里是你的物品背包",
            "可以存放武器、装备和道具",
            "点击物品查看详细属性"
        ]
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (50, 100 + i * 25))

# === Character 页面 ===
class CharacterPage(Page):
    def __init__(self, get_player_data):
        super().__init__("Character")
        self.get_player_data = get_player_data

    def draw(self, screen, font, player=None):
        character = load_image('assets/programmer.jpg',(736/4,736/4))
        screen.blit(character, (100, 100))
        title_font = get_font("Cogmind",30)
        content_font = get_font("DOS",20)
        text_surface = title_font.render("The harmful effect of programming", True, WHITE)
        screen.blit(text_surface, (50, 30))

        data = self.get_player_data()
        stats_lines = [
            f"HP: {data['health']}/{data['max_health']}",
            f"Sequence Limit: {data['sequence_limit']}",
            f"DP: {data['damage_multiplier']}",
        ]
        start_x, start_y = 50, 500
        line_height = content_font.get_height() + 5

        for i, line in enumerate(stats_lines):
            text_surface = content_font.render(line, True, WHITE)
            screen.blit(text_surface, (start_x, start_y + i * line_height))

        for i, (key, val) in enumerate(data['base_stats'].items()):
            stat_surface = content_font.render(f"{key}: {val}", True, WHITE)
            screen.blit(stat_surface, (400, start_y + i * line_height))

        self.draw_status(screen,content_font,500,100,data['status'])

    def draw_status(self,screen, font, x, y, status_list):
        # 先按 body_part 分类
        categorized = {}
        for s in status_list:
            # if s.is_illness:  # 只显示疾病类
                categorized.setdefault(s.body_part, []).append(s)

        current_y = y
        for body_part, illnesses in categorized.items():
            # 绘制部位标题
            part_text = font.render(f"{body_part.capitalize()}:", True, WHITE)
            screen.blit(part_text, (x, current_y))
            current_y += font.get_height() + 2

            # 绘制每个病
            for illness in illnesses:
                # 假设 illness 有 duration 属性
                name_line = f"{illness.name}({illness.stack},{illness.duration}t to reduce 1 layer)"
                illness_text = font.render(name_line, True, GREEN if illness.is_illness else WHITE)
                screen.blit(illness_text, (x + 20, current_y))
                current_y += font.get_height() + 2

            # 每个部位之间空一行
            current_y += 5

# === Settings 页面 ===
class SettingsPage(Page):
    def __init__(self):
        super().__init__("Settings")

    def draw(self, screen, font, player=None):
        content_lines = [
            "调整游戏设置和选项",
            "包括音效、画质和操作设置",
            "保存和加载游戏进度"
        ]
        for i, line in enumerate(content_lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (50, 100 + i * 25))

class Toolbar(PageContainer):
    def __init__(self, get_player_data):
        super().__init__("Toolbar", get_player_data, tab_pos=(50, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 10), direction="row")
        from AbilityTree import AbilityPage
        self.register_page(AbilityPage(get_player_data))
        self.register_page(InventoryPage())
        self.register_page(CharacterPage(get_player_data))
        self.register_page(SettingsPage())

    def create_tabs( self ,names, start_pos, direction="row", spacing=10):
        tabs = []
        x, y = start_pos
        
        for i, name in enumerate(names):
            if direction == "row":
                tab_x = x + i * (TAB_WIDTH + spacing)
                tab_y = y
            elif direction == "col":
                tab_x = x
                tab_y = y + i * (TAB_HEIGHT + spacing)
            else:
                raise ValueError("direction not valid")
            
            tab = Tab(name, tab_x, tab_y)
            tabs.append(tab)
        
        return tabs
