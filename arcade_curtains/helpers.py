from collections import defaultdict
from functools import partial, wraps

import arcade

from .animation import AnimationManagerProxy


def delay_set_attribute(sprite, flag, value):
    """
    helper function for setting an attribute of an object as a callback in a
    sequence or chain.
    """

    def _delay_set_attribute():
        setattr(sprite, flag, value)

    return _delay_set_attribute


def modified_init(orig_init):
    @wraps(orig_init)
    def init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.animate = AnimationManagerProxy(self)

    return init


def modified_kill(orig_kill):
    @wraps(orig_kill)
    def kill(self, *args, **kwargs):
        orig_kill(self, *args, **kwargs)
        self.animate.kill()

    return kill


class PositionHelperMixin:
    @property
    def topleft(self):
        return (self.left, self.top)

    @property
    def topright(self):
        return (self.right, self.top)

    @property
    def bottomleft(self):
        return (self.left, self.bottom)

    @property
    def bottomright(self):
        return (self.right, self.bottom)

    @topleft.setter
    def topleft(self, position):
        self.left, self.top = position

    @topright.setter
    def topright(self, position):
        self.right, self.top = position

    @bottomleft.setter
    def bottomleft(self, position):
        self.left, self.bottom = position

    @bottomright.setter
    def bottomright(self, position):
        self.right, self.bottom = position


class CurtainsMeta(type):
    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)
        self.__init__ = modified_init(self.__init__)
        self.kill = modified_kill(self.kill)


class Sprite(arcade.Sprite, PositionHelperMixin, metaclass=CurtainsMeta):
    pass


class TriggerAttr:
    def __init__(self, attribute):
        self.attribute = attribute

    def __eq__(self, other):
        return Trigger(self.attribute, '==', other)

    def __ne__(self, other):
        return Trigger(self.attribute, '!=', other)

    def __gt__(self, other):
        return Trigger(self.attribute, '>', other)

    def __ge__(self, other):
        return Trigger(self.attribute, '>=', other)

    def __lt__(self, other):
        return Trigger(self.attribute, '<', other)

    def __le__(self, other):
        return Trigger(self.attribute, '<=', other)


class Trigger:
    def __init__(self, attribute, op, value):
        """
        Nothing beats the speed of using relational operators, and getting
        attributes through dot accessing. Since this check might potentially
        be executed a good amount of times, we want to bake the check to be
        as fast as possible.
        """
        self.attribute = attribute
        self.op = op
        self.value = value

    def bake(self, obj):
        expression = "lambda s, x: s.{} {} {}".format(self.attribute, self.op,
                                                      self.value)
        self.check = partial(eval(expression), obj)

    def check(self, other):
        raise NotImplementedError(
            "Trigger is not yet baked. Call bake() first")


class ObservableSprite(Sprite):
    BEFORE_CHANGE = 0
    AFTER_CHANGE = 1
    TRIGGER = 2

    def __init__(self, *args, **kwargs):
        super().__setattr__(
            '_observe',
            defaultdict(lambda: [list(), list(), dict()]))
        super().__init__(*args, **kwargs)

    def __setattr__(self, key, value):
        if key in self._observe:
            old = getattr(self, key, None)
            handlers = self._observe[key]
            # Before handlers
            for handler in handlers[self.BEFORE_CHANGE]:
                handler(self, key, old, value)
            # Set the attribute
            super().__setattr__(key, value)
            # After handlers
            for handler in handlers[self.AFTER_CHANGE]:
                handler(self, key, old, value)
            # Triggers
            for check, handler in handlers[self.TRIGGER].items():
                if check(value):
                    handler()
        else:
            super().__setattr__(key, value)

    def observe(self, event_type, attribute, handler):
        self._observe[attribute][event_type].append(handler)

    def before_change(self, attribute, handler):
        self.observe(self.BEFORE_CHANGE, attribute, handler)

    def after_change(self, attribute, handler):
        self.observe(self.AFTER_CHANGE, attribute, handler)

    def trigger(self, trigger, handler):
        trigger.bake(self)
        self._observe[trigger.attribute][self.TRIGGER][trigger.check] = handler


class AnchorPoint:
    def __init__(self, center_x, center_y):
        self._center_x = center_x
        self._center_y = center_y
        self.boats = set()

    def dock(self, boat):
        self.boats.add(boat)

    @property
    def center_x(self):
        return self._center_x

    @property
    def center_y(self):
        return self._center_y

    @property
    def position(self):
        return self.center_x, self.center_y

    @center_x.setter
    def center_x(self, value):
        offset = value - self._center_x
        self._center_x = value
        for boat in self.boats:
            boat.center_x += offset

    @center_y.setter
    def center_y(self, value):
        offset = value - self._center_y
        self._center_y = value
        for boat in self.boats:
            boat.center_y += offset

    @position.setter
    def position(self, value):
        self.center_x, self.center_y = value

    @classmethod
    def from_sprite(cls, sprite, orientation):
        anchor = cls(*getattr(sprite, orientation))
        anchor.dock(sprite)
        return anchor


class Widget(PositionHelperMixin):
    def __init__(self, center_x=0, center_y=0, **kwargs):
        self.sprites = []
        self.setup_widget(**kwargs)
        self.anchor = AnchorPoint(
            center_x=self.center_x, center_y=self.center_y)
        for sprite in self.sprites:
            self.anchor.dock(sprite)
        self.anchor.position = (center_x, center_y)
        self.post_setup()

    def setup_widget(self):
        raise NotImplementedError()

    def post_setup(self):
        pass

    def _get_widget_bounds(self):
        return self._get_x_bounds, self._get_y_bounds

    def _get_y_bounds(self):
        if not self.sprites:
            return (0, 0)
        top = self.sprites[0].top
        bottom = self.sprites[0].bottom
        for sprite in self.sprites[1:]:
            top = max(top, sprite.top)
            bottom = min(bottom, sprite.bottom)
        return top, bottom

    def _get_x_bounds(self):
        if not self.sprites:
            return (0, 0)
        left = self.sprites[0].left
        right = self.sprites[0].right
        for sprite in self.sprites[1:]:
            left = min(left, sprite.left)
            right = max(right, sprite.right)
        return left, right

    @property
    def position(self):
        return self.center_x, self.center_y

    @position.setter
    def position(self, value):
        self.center_x, self.center_y = value

    @property
    def center_x(self):
        left, right = self._get_x_bounds()
        return ((right - left) / 2) + left

    @center_x.setter
    def center_x(self, value):
        self.anchor.center_x = value

    @property
    def center_y(self):
        top, bottom = self._get_y_bounds()
        return ((top - bottom) / 2) + bottom

    @center_y.setter
    def center_y(self, value):
        self.anchor.center_y = value

    @property
    def left(self):
        left, right = self._get_x_bounds()
        return left

    @left.setter
    def left(self, value):
        offset = value - self.left
        self.anchor.center_x += offset

    @property
    def right(self):
        left, right = self._get_x_bounds()
        return right

    @right.setter
    def right(self, value):
        offset = value - self.right
        self.anchor.center_x += offset

    @property
    def top(self):
        top, bottom = self._get_y_bounds()
        return top

    @top.setter
    def top(self, value):
        offset = value - self.top
        self.anchor.center_y += offset

    @property
    def bottom(self):
        top, bottom = self._get_y_bounds()
        return bottom

    @bottom.setter
    def bottom(self, value):
        offset = value - self.bottom
        self.anchor.center_y += offset

    @property
    def width(self):
        left, right = self._get_x_bounds()
        return right - left

    @property
    def height(self):
        top, bottom = self._get_y_bounds()
        return top - bottom

    def register(self, spritelist):
        for sprite in self.sprites:
            spritelist.append(sprite)


arcade.Sprite = Sprite
arcade.sprite.Sprite = Sprite
