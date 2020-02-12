from functools import wraps

import arcade
from pyglet import clock

from .scene import BaseScene  # noqa
from .animation import Sequence, KeyFrame, Chain  # noqa
from .helpers import (  # noqa
    PositionHelperMixin, Sprite, ObservableSprite, AnchorPoint, Widget)


def bind(fn, window_fn):
    @wraps(window_fn)
    def decorator(*args, **kwargs):
        res = window_fn(*args, **kwargs)
        fn(*args, **kwargs)
        return res

    return decorator


class Curtains:
    def __init__(self, window=None):
        self.current_scene = None
        self.window = None
        self.scenes = {}
        if window:
            self.bind(window)

    def add_scene(self, name, scene):
        self.scenes[name] = scene
        scene._bind(self.window, self)

    def add_scenes(self, scenes):
        for name, scene in scenes.items():
            self.add_scene(name, scene)

    def set_scene(self, name):
        if self.current_scene:
            self.current_scene.leave_scene(self.scenes[name])
        previous_scene = self.current_scene
        self.current_scene = self.scenes[name]
        self.current_scene.enter_scene(previous_scene)

    def bind(self, window=None):
        if window:
            self.window = window
            self.window.curtains = self
            for scene in self.scenes.values():
                scene._bind(self.window, self)
        if not self.window:
            msg = "Curtains instance is not yet bound to an Arcade window"
            raise Exception(msg)

        clock.unschedule(window.update)
        members = {
            'update': self.update,
            'on_draw': self.on_draw,
            'on_mouse_motion': self.on_mouse_motion,
            'on_mouse_press': self.on_mouse_press,
            'on_mouse_release': self.on_mouse_release,
            'on_mouse_drag': self.on_mouse_drag,
            'on_key_press': self.on_key_press
        }
        for member, fn in members.items():
            window_fn = getattr(window, member)
            setattr(window, member, bind(fn, window_fn))
        # clock.schedule(window.update)
        clock.schedule_interval(window.update, 1 / 60)

    def on_draw(self):
        arcade.start_render()

        self.current_scene.events.trigger_before_draw()
        self.current_scene.draw()
        self.current_scene.events.trigger_after_draw()

    def update(self, delta_time):
        self.current_scene.events.trigger_frame(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        self.current_scene.events.update(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.current_scene.events.trigger_down(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.current_scene.events.trigger_up(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.current_scene.events.trigger_drag(x, y, dx, dy)

    def on_key_press(self, key, modifiers):
        if not modifiers:
            self.current_scene.events.trigger_key_press(key)
