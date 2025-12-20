from collections import deque
from colors import *

class Event:
    pass


class EventQueue:
    def __init__(self):
        self.queue = deque()

    def push(self, event):
        self.queue.append(event)

    def pop(self):
        return self.queue.popleft() if self.queue else None

    def empty(self):
        return not self.queue
    

class DamageEvent(Event):
    def __init__(self, source, target, amount):
        self.source = source
        self.target = target
        self.amount = amount


class DeathEvent(Event):
    def __init__(self, pawn):
        self.pawn = pawn


class MessageEvent(Event):
    def __init__(self, text, color=WHITE):
        self.text = text
        self.color = color

