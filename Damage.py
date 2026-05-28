class Damage:
    def __init__(self, value: int):
        self._value = value

    def value(self) -> int:
        return self._value

class DamageDecorator(Damage):
    def __init__(self, inner: Damage):
        self.inner = inner

    def value(self) -> int:
        return self.inner.value()

class DDLFeverDecorator(DamageDecorator):
    def __init__(self, inner: Damage, player):
        super().__init__(inner)
        self.player = player

    def value(self) -> int:
        v = self.inner.value()

        # 示例条件：血量 < 50%
        if self.player.health / self.player.max_health < 0.5:
            print("DDL fever 触发，伤害增加 3")
            return v + 3  # DDL fever 是加算，很合理

        return v

