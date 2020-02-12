import arcade

from .event import EventHandler
from .animation import AnimationManager


class BaseScene:
    def __init__(self, *args, **kwargs):
        self.window = None
        self.curtains = None
        self.animations = AnimationManager()
        self.events = EventHandler()
        self.events.frame(self.animations._blip)
        self._sprite_lists = []
        self.setup(*args, **kwargs)
        self._setup_spritelists()

    def _bind(self, window, curtains):
        self.window = window
        self.curtains = curtains

    def setup(self, *args, **kwargs):
        raise NotImplementedError()

    def leave_scene(self, next_scene):
        pass

    def enter_scene(self, previous_scene):
        pass

    def _setup_spritelists(self):
        for attribute in dir(self):
            attr = getattr(self, attribute)
            if isinstance(attr, arcade.SpriteList):
                self._sprite_lists.append(attr)

    def draw(self):
        for slist in self._sprite_lists:
            slist.draw()
