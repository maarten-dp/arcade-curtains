import weakref
import arcade
from unittest.mock import Mock
import time
from enum import Enum
from collections import defaultdict
from functools import partialmethod


class SpriteEvent(Enum):
    CLICK = 1
    OUT = 2
    HOVER = 3
    DOWN = 4
    UP = 5
    DRAG = 6


class Event(Enum):
    FRAME = 7
    BEFORE_DRAW = 8
    AFTER_DRAW = 9
    ESCAPE = 10


EMPTY = Mock()
EMPTY_SPRITE = Mock()


class EventHandler(object):
    def __init__(self):
        self.sprite_handlers = defaultdict(dict)
        self.handlers = defaultdict(list)

        self.all_sprites = []

        self._previous_hover = EMPTY_SPRITE
        self._previous_down = EMPTY_SPRITE

        self.current_x = 0
        self.current_y = 0

    def update(self, x, y):
        self.current_x = x
        self.current_y = y
        current_hover = self.get_sprite_at(x, y)
        if current_hover is not self._previous_hover:
            self.sprite_handlers[SpriteEvent.OUT].get(self._previous_hover, EMPTY)(self._previous_hover, x, y)
            self.sprite_handlers[SpriteEvent.HOVER].get(current_hover, EMPTY)(current_hover, x, y)
            self._previous_hover = current_hover

    def trigger_down(self, x, y):
        current_down = self.get_sprite_at(x, y)
        self.sprite_handlers[SpriteEvent.DOWN].get(current_down, EMPTY)(current_down, x, y)
        self._previous_down = current_down

    def trigger_up(self, x, y):
        current_up = self.get_sprite_at(x, y)
        self.sprite_handlers[SpriteEvent.UP].get(current_up, EMPTY)(current_up, x, y)
        if current_up is self._previous_down:
            self.sprite_handlers[SpriteEvent.CLICK].get(current_up, EMPTY)(current_up, x, y)
        self._previous_down = EMPTY_SPRITE

    def trigger_drag(self, x, y, dx, dy):
        self.sprite_handlers[SpriteEvent.DRAG].get(self._previous_down, EMPTY)(self._previous_down, x, y, dx, dy)

    def trigger_frame(self, delta_time):
        for handler in self.handlers[Event.FRAME]:
            handler(delta_time)

    def trigger_before_draw(self):
        for handler in self.handlers[Event.BEFORE_DRAW]:
            handler()

    def trigger_after_draw(self):
        for handler in self.handlers[Event.AFTER_DRAW]:
            handler()

    def trigger_escape(self):
        for handler in self.handlers[Event.ESCAPE]:
            handler()

    def get_sprite_at(self, *coords):
        sprites = arcade.get_sprites_at_point(coords, self.all_sprites)
        if sprites:
            return max(sprites)
        return EMPTY_SPRITE

    def add_sprite_event(self, event_type, sprite, handler_function):
        self.all_sprites.append(sprite)
        self.all_sprites = list(set(self.all_sprites))
        self.sprite_handlers[event_type][sprite] = handler_function

    def add_event(self, event_type, handler_function):
        if handler_function not in self.handlers[event_type]:
            self.handlers[event_type].append(handler_function)

    def remove_sprite_event(self, event_type, sprite):
        if self.sprite_handlers[event_type].get(sprite, None):
            del self.sprite_handlers[event_type][sprite]
            if self._previous_hover == sprite:
                self._previous_hover = EMPTY_SPRITE
            if self._previous_down == sprite:
                self._previous_down = EMPTY_SPRITE

    def remove_event(self, event_type, handler):
        while handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    def remove_from_all(self, handler):
        for event_type, handlers in self.handlers.items():
            if handler in handlers:
                self.remove_event(event_type, handler)

    def kill(self, sprite):
        for event in SpriteEvent:
            self.remove_sprite_event(event, sprite)
        for attribute_name in dir(sprite):
            attr = getattr(sprite, attribute_name)
            if callable(attr):
                for event in Event:
                    self.remove_event(event, attr)
        if sprite in self.all_sprites:
            self.all_sprites.remove(sprite)

    click = partialmethod(add_sprite_event, SpriteEvent.CLICK)
    hover = partialmethod(add_sprite_event, SpriteEvent.HOVER)
    out = partialmethod(add_sprite_event, SpriteEvent.OUT)
    down = partialmethod(add_sprite_event, SpriteEvent.DOWN)
    up = partialmethod(add_sprite_event, SpriteEvent.UP)
    drag = partialmethod(add_sprite_event, SpriteEvent.DRAG)
    frame = partialmethod(add_event, Event.FRAME)
    before_draw = partialmethod(add_event, Event.BEFORE_DRAW)
    after_draw = partialmethod(add_event, Event.AFTER_DRAW)
    escape = partialmethod(add_event, Event.ESCAPE)
