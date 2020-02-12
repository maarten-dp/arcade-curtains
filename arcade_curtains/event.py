from collections import defaultdict
from enum import Enum
from functools import partialmethod
from unittest.mock import Mock

import arcade


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


EMPTY_SPRITE = Mock()


def run_handlers(handlers, *args, **kwargs):
    for handler, handler_kwargs in handlers:
        kwargs.update(handler_kwargs)
        handler(*args, **kwargs)


class EventHandler(object):
    def __init__(self):
        self.sprite_handlers = defaultdict(lambda: defaultdict(list))
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
            self.trigger_hover_out(self._previous_hover, x, y)
            self.trigger_hover(current_hover, x, y)
            self._previous_hover = current_hover

    def trigger_hover_out(self, sprite, x, y):
        handlers = self.sprite_handlers[SpriteEvent.OUT].get(sprite, [])
        run_handlers(handlers, sprite, x, y)

    def trigger_hover(self, sprite, x, y):
        handlers = self.sprite_handlers[SpriteEvent.HOVER].get(sprite, [])
        run_handlers(handlers, sprite, x, y)

    def trigger_down(self, x, y):
        current_down = self.get_sprite_at(x, y)
        handlers = self.sprite_handlers[SpriteEvent.DOWN].get(current_down, [])
        run_handlers(handlers, current_down, x, y)
        self._previous_down = current_down

    def trigger_up(self, x, y):
        current_up = self.get_sprite_at(x, y)
        handlers = self.sprite_handlers[SpriteEvent.UP].get(current_up, [])
        run_handlers(handlers, current_up, x, y)
        if current_up is self._previous_down:
            self.trigger_click(current_up, x, y)
        self._previous_down = EMPTY_SPRITE

    def trigger_click(self, sprite, x, y):
        handlers = self.sprite_handlers[SpriteEvent.CLICK].get(sprite, [])
        run_handlers(handlers, sprite, x, y)

    def trigger_drag(self, x, y, dx, dy):
        drag_sprites = self.sprite_handlers[SpriteEvent.DRAG]
        handlers = drag_sprites.get(self._previous_down, [])
        run_handlers(handlers, self._previous_down, x, y, dx, dy)

    def trigger_frame(self, delta_time):
        run_handlers(self.handlers[Event.FRAME], delta_time)

    def trigger_before_draw(self):
        run_handlers(self.handlers[Event.BEFORE_DRAW])

    def trigger_after_draw(self):
        run_handlers(self.handlers[Event.AFTER_DRAW])

    def trigger_key_press(self, key):
        run_handlers(self.handlers.get(key, []))

    def get_sprite_at(self, *coords):
        sprites = arcade.SpriteList()
        sprites.sprite_list = self.all_sprites
        sprites = arcade.get_sprites_at_point(coords, sprites)
        if sprites:
            return max(sprites)
        return EMPTY_SPRITE

    def add_sprite_event(self, event_type, sprite, handler_function,
                         kwargs={}):
        self.all_sprites.append(sprite)
        self.all_sprites = list(set(self.all_sprites))
        self.sprite_handlers[event_type][sprite].append((handler_function,
                                                         kwargs))

    def add_event(self, event_type, handler_function, kwargs={}):
        if handler_function not in self.handlers[event_type]:
            self.handlers[event_type].append((handler_function, kwargs))

    def remove_sprite_event(self, event_type, sprite, handler):
        if self.sprite_handlers[event_type].get(sprite, None):
            for details in self.sprite_handlers[event_type][sprite]:
                if details[0] == handler:
                    self.sprite_handlers[event_type][sprite].remove(details)

    def remove_event(self, event_type, handler):
        for details in self.handlers[event_type]:
            if details[0] == handler:
                self.handlers[event_type].remove(details)

    def remove_from_all(self, handler):
        for event_type, handlers in self.handlers.items():
            self.remove_event(event_type, handler)

    def kill(self, sprite):
        for event in SpriteEvent:
            self.sprite_handlers[event].pop(sprite, None)
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

    remove_click = partialmethod(remove_sprite_event, SpriteEvent.CLICK)
    remove_hover = partialmethod(remove_sprite_event, SpriteEvent.HOVER)
    remove_out = partialmethod(remove_sprite_event, SpriteEvent.OUT)
    remove_down = partialmethod(remove_sprite_event, SpriteEvent.DOWN)
    remove_up = partialmethod(remove_sprite_event, SpriteEvent.UP)
    remove_drag = partialmethod(remove_sprite_event, SpriteEvent.DRAG)
    remove_frame = partialmethod(remove_event, Event.FRAME)
    remove_before_draw = partialmethod(remove_event, Event.BEFORE_DRAW)
    remove_after_draw = partialmethod(remove_event, Event.AFTER_DRAW)

    key = add_event
    remove_key = remove_event
