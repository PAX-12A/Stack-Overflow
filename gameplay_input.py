# gameplay_input.py

import pygame

from grid import Vec2

from commands import (
    MoveCommand,
    WaitCommand,
    ExecuteSequenceCommand,
    RotateCommand,
)
from Action import PlayerEndTurnAction


class GameplayInputSystem:

    def __init__(self, scene):

        self.scene = scene

        # key -> command builder
        self.keymap = {

            # ===== Move =====

            pygame.K_a:
                lambda: MoveCommand(Vec2(-1, 0)),

            pygame.K_LEFT:
                lambda: MoveCommand(Vec2(-1, 0)),

            pygame.K_d:
                lambda: MoveCommand(Vec2(1, 0)),

            pygame.K_RIGHT:
                lambda: MoveCommand(Vec2(1, 0)),

            # ===== Rotate =====

            pygame.K_w:
                lambda: RotateCommand(),

            pygame.K_UP:
                lambda: RotateCommand(),

            # ===== Wait =====

            pygame.K_s:
                lambda: WaitCommand(),

            pygame.K_DOWN:
                lambda: WaitCommand(),

            # ===== Execute Sequence =====

            pygame.K_x:
                lambda: ExecuteSequenceCommand(),

            pygame.K_SPACE:
                lambda: ExecuteSequenceCommand(),
        }

    # ======================================================
    # Main Input Entry
    # ======================================================

    def handle_event(self, event):

        if self.scene.game_state != "player_turn":
            return False

        if event.type != pygame.KEYDOWN:
            return False

        builder = self.keymap.get(event.key)

        if builder is None:
            return False

        command = builder()

        return self.execute_command(command)

    # ======================================================
    # Execute Command
    # ======================================================

    def execute_command(self, command):

        if self.scene.input_locked: #防止玩家快速点击入队多个动作
            return False

        # Build actions from command
        command.build_actions(self.scene)

        # Resolve action queue
        consumed = self.scene.resolve_actions()

        # End turn if consumed
        if consumed:
            self.scene.actions.append(PlayerEndTurnAction(self.scene.player))

        return consumed