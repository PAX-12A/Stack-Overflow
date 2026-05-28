# ui_input.py

import pygame

from commands import (
    SelectWeaponCommand,
    ReorderSequenceCommand,
    AddWeaponToSequenceCommand
)

from hotbar import WeaponHotbar


class UIInputSystem:

    def __init__(self, scene):

        self.scene = scene

        # ==========================================
        # Hotbar
        # ==========================================

        self.hotbar = WeaponHotbar()

        # ==========================================
        # Dragging State
        # ==========================================

        self.dragging_weapon = None
        self.dragging_index = None

    # ======================================================
    # Main Event Entry
    # ======================================================

    def handle_event(self, event):

        # ==========================================
        # Hotbar
        # ==========================================

        command = self.hotbar.handle_event(event)

        if command:

            self.execute_ui_command(command)

            return True

        # ==========================================
        # Sequence Mouse Input
        # ==========================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            return self.handle_mouse_down(event)

        elif event.type == pygame.MOUSEBUTTONUP:

            return self.handle_mouse_up(event)

        return False

    # ======================================================
    # Mouse Down
    # ======================================================

    def handle_mouse_down(self, event):

        mx, my = event.pos

        player = self.scene.player

        # ==========================================
        # Add weapon to sequence
        # ==========================================

        for i in range(len(player.weapons)):

            rect = self.scene.get_weapon_rect(i)

            if rect.collidepoint(mx, my):

                command = AddWeaponToSequenceCommand(i)

                self.execute_ui_command(command)

                return True

        # ==========================================
        # Start dragging sequence
        # ==========================================

        for i, index in enumerate(player.action_sequence):

            rect = self.scene.get_sequence_rect(i)

            if rect.collidepoint(mx, my):

                self.dragging_index = i
                self.dragging_weapon = index

                return True

        return False

    # ======================================================
    # Mouse Up
    # ======================================================

    def handle_mouse_up(self, event):

        if self.dragging_weapon is None:
            return False

        mx, my = event.pos

        player = self.scene.player

        new_index = None

        for i in range(len(player.action_sequence)):

            rect = self.scene.get_sequence_rect(i)

            if rect.collidepoint(mx, my):

                new_index = i
                break

        if new_index is not None:

            command = ReorderSequenceCommand(
                self.dragging_index,
                new_index
            )

            self.execute_ui_command(command)

        # reset dragging
        self.dragging_weapon = None
        self.dragging_index = None

        return True

    # ======================================================
    # Execute UI Command
    # ======================================================

    def execute_ui_command(self, command):

        player = self.scene.player

        # ==========================================
        # Select weapon
        # ==========================================

        if isinstance(command, SelectWeaponCommand):

            if command.index < len(player.weapons):

                self.hotbar.selected_index = command.index

                # print(command.index)

        # ==========================================
        # Reorder sequence
        # ==========================================

        elif isinstance(command, ReorderSequenceCommand):

            seq = player.action_sequence

            weapon = seq.pop(command.old_index)

            seq.insert(command.new_index, weapon)

        # ==========================================
        # Add weapon to sequence
        # ==========================================

        elif isinstance(command, AddWeaponToSequenceCommand):

            success, msg = (
                player.try_add_weapon_to_sequence(
                    command.weapon_index,
                    self.scene
                )
            )

            self.scene.add_message(msg)

            if success:

                self.scene.end_player_turn()

    # ======================================================
    # Update
    # ======================================================

    def update(self):

        player = self.scene.player

        self.hotbar.set_weapons(player.weapons)

    # ======================================================
    # Draw
    # ======================================================

    def draw(self, screen, font):

        self.hotbar.draw(screen, font)