class MoveAbility:
    def can_move_to(self, pos, gamemap) -> bool:
        raise NotImplementedError

    def can_spawn_at(self, pos, gamemap) -> bool:
        # 默认和移动判断一致，子类可以覆盖
        return self.can_move_to(pos, gamemap)

    def _no_trap(self, pos, gamemap) -> bool:
        return gamemap.get_trap(pos) is None

    def _not_occupied(self, pos, gamemap) -> bool:
        return not gamemap.is_occupied(pos)


class GroundMove(MoveAbility):
    def can_move_to(self, pos, gamemap) -> bool:
        return (
            not gamemap.is_wall(pos)
            and self._not_occupied(pos, gamemap)
            and self._no_trap(pos, gamemap)    # 地面生物不走陷阱
        )


class FlyingMove(MoveAbility):
    def can_move_to(self, pos, gamemap) -> bool:
        return (
            not gamemap.is_wall(pos)
            and self._not_occupied(pos, gamemap)
            # 飞行生物不受陷阱影响
        )