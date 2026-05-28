import pygame
import sys
from fight import *
from util import *
from pages import *

# 初始化pygame
pygame.init()

pygame.mixer.init()  # 初始化音频系统
# 载入背景音乐
# try:
#     pygame.mixer.mu
# ic.load("assets/music/illusion.mp3")  # 音乐文件路径
#     pygame.mixer.music.set_volume(0)  # 设置音量（0.0 到 1.0）
#     pygame.mixer.music.play(-1)  # -1 表示循环播放


# except pygame.error as e:
#     print(f"无法载入背景音乐: {e}")

class MainMenu:
    def __init__(self, font):
        self.font = font
        self.options = ["Start", "Help", "Quit"]
        self.selected = 0 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]
            
        return None

    def draw(self, screen):
        screen.fill(BLACK)

        menu_font = get_font("Patriot",32)
        opt_font = get_font("Cogmind",20)
        title_surface = menu_font.render("Stack OverflOw", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_surface, title_rect)

        for i, option in enumerate(self.options):
            color=WHITE
            if i == self.selected:
                color = GREEN 
                pic = f"girl{i+1}"
                render_ascii_art(screen, label=pic, font_size=16, x=150, y=-70, color=WHITE)

            image = load_image(f"arts/sprite/{self.options[i]}.png",(32,32))
            render_1bit_sprite(screen, image, (190, 135 + i*50 - image.get_width()//2), color)
            icon = load_image(f"arts/stack.png",(64,64))
            screen.blit(icon,(25,25))

            text_surface = opt_font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 140 + i*50))
            screen.blit(text_surface, text_rect)
            

    def intro(self,screen):
        screen.fill(BLACK)
        welcome = load_image(f"arts/terminal of life.png")
        screen.blit(welcome,((SCREEN_WIDTH-welcome.get_width())//2,100))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay,((SCREEN_WIDTH-welcome.get_width())//2,100))

        intro_text = [
        "Welcome to Stack Overflow",
        "In the game,Programming language is your sword,",
        
        "and your brain is the shield.",
        "Here is a simple tutorial:",
        "A,D for move ,",
        "S to end your turn.", 
        "W to turn around,"
        "X/Space to execute sequence",
        "Don't make your brain 'Stack Overflow'.",
        ]
        self.draw_multiline_dialog(screen,intro_text,self.font)

    def draw_text(self,screen,text, x, y, font, color=WHITE):
        rendered = font.render(text, True, color)
        screen.blit(rendered, (x, y))

    # 像视觉小说一样显示文字
    def draw_multiline_dialog(self,screen, text_lines, font ,start_y=40, color=WHITE, line_spacing=20):
        
        self.draw_text(screen,"Press ENTER to continue...", 20, SCREEN_HEIGHT - 30,font,GREEN)

        line_index = 0
        self.draw_text(screen,text_lines[line_index], 40, start_y + line_index * line_spacing, font,color)
        line_index += 1

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if line_index < len(text_lines):
                        self.draw_text(screen,text_lines[line_index], 50,start_y + line_index * line_spacing, font,color)
                        line_index += 1
                        pygame.display.flip()
                    else:
                        waiting = False

class GameApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE)
        self.base_size = (SCREEN_WIDTH, SCREEN_HEIGHT)  # 你的设计分辨率
        self.virtual_surface = pygame.Surface(self.base_size)
        self.window_size = self.screen.get_size()

        pygame.display.set_caption("Stack Overflow")
        self.clock = pygame.time.Clock()

        self.font_en = get_font("Cogmind", 10)
        self.font_ch = get_font("Pixel", 10)

        self.menu = MainMenu(self.font_en)
        self.scene = FightScene()
        self.toolbar = Toolbar(self.scene.get_player_data)

        SkillLibrary.init_skills()
        self.state = MenuState(self)

        self.running = True
        is_fullscreen = False

class GameState:
    def handle_event(self, event): pass
    def update(self): pass
    def draw(self): pass

class MenuState(GameState):
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        choice = self.app.menu.handle_event(event)
        if choice == "Start":
            self.app.menu.intro(self.app.screen)
            self.app.state = PlayingState(self.app)
        elif choice == "Quit":
            self.app.running = False

    def draw_to(self, surface):
        self.app.menu.draw(surface)

class PlayingState(GameState):
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        scene = self.app.scene
        toolbar = self.app.toolbar

        toolbar.handle_event(event, scene.player)
        scene.handle_event(event)


    def update(self):
        self.app.toolbar.update(self.app.scene.player)
        self.app.scene.update()

        if self.app.scene.game_state == "game_over":
            self.app.state = GameOverState(self.app)

    def draw_to(self, surface):
        surface.fill(BLACK)

        self.app.scene.draw(surface)

        self.app.toolbar.draw(
            surface,
            self.app.font_ch,
            self.app.scene.get_player_data()
        )


        pygame.display.flip() 

class GameOverState(GameState):
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.app.scene = FightScene()
                self.app.state = MenuState(self.app)
            elif event.key == pygame.K_r:
                self.app.scene = FightScene()
                self.app.state = PlayingState(self.app)

    def draw_to(self, surface):
        self.app.scene.draw(surface)
        
def main():
    pygame.init()
    app = GameApp()

    while app.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            elif event.type == pygame.VIDEORESIZE:
                app.window_size = (event.w, event.h)
                app.screen = pygame.display.set_mode(app.window_size, pygame.RESIZABLE)
            else:
                app.state.handle_event(event)

        app.state.update()
        # app.state.draw()
        # # print(app.state.__class__.__name__)

        # pygame.display.flip()
        # 1. 所有内容画到虚拟画布
        app.virtual_surface.fill((0,0,0))
        app.state.draw_to(app.virtual_surface)

        # 2. 等比缩放 + 黑边
        screen_w, screen_h = app.window_size
        base_w, base_h = app.base_size

        scale = min(screen_w / base_w, screen_h / base_h)//1
        new_w = int(base_w * scale)
        new_h = int(base_h * scale)

        offset_x = (screen_w - new_w) // 2
        offset_y = (screen_h - new_h) // 2

        scaled = pygame.transform.scale(app.virtual_surface, (new_w, new_h))

        app.screen.fill((0,0,0))
        app.screen.blit(scaled, (offset_x, offset_y))

        pygame.display.flip()
        app.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()