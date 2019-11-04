import arcade

from .event import EventHandler


class BaseScene:
    def __init__(self):
        self.window = None
        self.curtains = None
        self.events = EventHandler()
        self._sprite_lists = []
        self.setup()
        self._setup_spritelists()

    def _bind(self, window, curtains):
        self.window = window
        self.curtains = curtains

    def setup(self):
        raise NotImplementedError()

    def leave_scene(self):
        pass

    def enter_scene(self):
        pass

    def _setup_spritelists(self):
        for attribute in dir(self):
            attr = getattr(self, attribute)
            if isinstance(attr, arcade.SpriteList):
                self._sprite_lists.append(attr)

    def draw(self):
        for slist in self._sprite_lists:
            slist.draw()
