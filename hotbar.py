# hotbar.py
import pygame
from pages import Tab, Page
from util import *
from commands import SelectWeaponCommand,AddWeaponToSequenceCommand

SLOT_SIZE = 42        # 每格尺寸（比 TAB 稍大）
SLOT_SPACING = 0
MAX_SLOTS = 9         # MC 经典 9 格

class WeaponSlotTab(Tab):
    """继承 Tab，但额外支持冷却遮罩和选中高亮。"""
    
    def __init__(self, index, x, y, size=SLOT_SIZE):
        super().__init__(str(index + 1), x, y, tab_width=size, tab_height=size, text=False)
        self.index = index
        self.weapon = None          # 绑定的武器对象
        self.size = size

    def draw(self, screen, font, is_selected=False):
        weapon = self.weapon

        # —— 1. 底色：复用父类逻辑 ——
        self.is_active = is_selected
        super().draw(screen, font, img=False)   # 画槽底（黑/白/灰+白边框）

        if weapon is None:
            return

        # —— 2. 武器图标 ——
        color = GREEN if weapon.is_ready() else RED
        try:
            icon = load_image(f"arts/sprite/weapons/{weapon.name}.png", (32, 32))
            render_1bit_sprite(screen, icon, (self.rect.x + 8, self.rect.y + 8), color)
        except Exception:
            pass

        # —— 3. 冷却遮罩（从底部往上填充，类 MC 风格）——
        if not weapon.is_ready():
            ratio = weapon.current_cooldown / weapon.cooldown   # 0=Ready, 1=Full CD
            overlay_h = int(self.size * ratio)
            overlay = pygame.Surface((self.size, overlay_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (self.rect.x, self.rect.y + self.size - overlay_h))

        # —— 4. 数字角标 ——
        num_surf = font.render(str(self.index + 1), True, GRAY)
        screen.blit(num_surf, (self.rect.x + 2, self.rect.y + 30))

        # —— 5. 武器名（选中时显示在槽上方）——
        if is_selected:
            name_surf = font.render(f"{weapon.name}", True, GREEN)
            screen.blit(name_surf, (self.rect.centerx - name_surf.get_width() // 2,
                                    self.rect.y - name_surf.get_height() - 2))
        
        # 武器伤害
        dam_surf = font.render(f"{weapon.damage}", True, GREEN)
        screen.blit(dam_surf, (self.rect.x + 2, self.rect.y + 2))

class WeaponHotbar(Page):
    """
    MC 风格武器快捷栏。
    放在屏幕底部居中，支持数字键/滚轮切换。
    """

    def __init__(self, get_player_data=None):
        super().__init__("WeaponHotbar")
        self.selected_index = 0
        self.slots: list[WeaponSlotTab] = []
        self._build_slots()

    # 构建槽位 
    def _build_slots(self):
        total_w = MAX_SLOTS * SLOT_SIZE + (MAX_SLOTS - 1) * SLOT_SPACING
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = SCREEN_HEIGHT - SLOT_SIZE - 2   # 距底 2px

        self.slots = [
            WeaponSlotTab(i,
                          start_x + i * (SLOT_SIZE + SLOT_SPACING),
                          start_y)
            for i in range(MAX_SLOTS)
        ]

    # # 同步武器列表 → 槽位 
    # def _sync_weapons(self, player):
    #     for i, slot in enumerate(self.slots):
    #         slot.weapon = player.weapons[i] if i < len(player.weapons) else None

    def set_weapons(self, weapons):

        for i, slot in enumerate(self.slots):

            slot.weapon = (
                weapons[i]
                if i < len(weapons)
                else None
            )

    def handle_event(self, event):

        # 数字键
        if event.type == pygame.KEYDOWN:

            for i in range(MAX_SLOTS):

                if event.key == getattr(pygame, f"K_{i+1}"):

                    self.selected_index = i

                    return AddWeaponToSequenceCommand(i)

        # 滚轮
        if event.type == pygame.MOUSEWHEEL:

            self.selected_index = (
                self.selected_index - event.y
            ) % MAX_SLOTS

            return SelectWeaponCommand(
                self.selected_index
            )

        # 点击
        if event.type == pygame.MOUSEBUTTONDOWN:

            for slot in self.slots:

                if slot.rect.collidepoint(event.pos):

                    self.selected_index = slot.index

                    return SelectWeaponCommand(
                        slot.index
                    )

        return None

    def draw(self, screen, font):
        # print(self.selected_index)
        for i, slot in enumerate(self.slots):
            # print(i == self.selected_index)
            slot.draw(screen, font, is_selected=(i == self.selected_index))