# commands.py

from Action import (
    MoveAction,
    WaitAction
)

from grid import Vec2


class Command:
    pass


# =========================================================
# Move
# =========================================================

class MoveCommand(Command):

    def __init__(self, direction):

        self.direction = direction

    def build_actions(self, scene):

        scene.actions.append(
            MoveAction(
                scene.player,
                self.direction
            )
        )


# =========================================================
# Wait
# =========================================================

class WaitCommand(Command):

    def build_actions(self, scene):

        scene.actions.append(
            WaitAction(scene.player)
        )


# =========================================================
# Rotate
# =========================================================

class RotateCommand(Command):

    def build_actions(self, scene):

        scene.player.turn_around()

        # 原地转向也算消耗回合
        scene.actions.append(
            WaitAction(scene.player)
        )


# =========================================================
# Execute Sequence
# =========================================================

class ExecuteSequenceCommand(Command):

    def build_actions(self, scene):

        player = scene.player

        if not player.action_sequence:

            scene.add_message("Empty Sequence!")

            return

        scene.execute_actions(player)


# class SelectWeaponCommand(Command):

#     def __init__(self, index):

#         self.index = index

#     def build_actions(self, scene):

#         player = scene.player

#         player.current_weapon_index = self.index
#         print ("666")

#         scene.execute_actions(player)

# =========================================================
# UI Commands
# =========================================================

class SelectWeaponCommand(Command):

    def __init__(self, index):

        self.index = index


class ReorderSequenceCommand(Command):

    def __init__(self, old_index, new_index):

        self.old_index = old_index
        self.new_index = new_index


class AddWeaponToSequenceCommand(Command):

    def __init__(self, weapon_index):

        self.weapon_index = weapon_index