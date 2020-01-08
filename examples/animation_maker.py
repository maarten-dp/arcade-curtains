import math
import arcade

from arcade_curtains import Curtains, BaseScene, Sequence, KeyFrame
from example_helpers import TabGroup, RadioGroup, SquareSprite, Button

WHITE = arcade.color.WHITE
GREEN = arcade.color.GREEN
BRICK_RED = arcade.color.BRICK_RED
TEAL = arcade.color.TEAL


def to_valid_bound(value, minval, maxval):
    if value > maxval:
        value = maxval
    if value < minval:
        value = minval
    return value


class AnimationDetails:
    def __init__(self):
        self.keyframes = {}
        self.current_keyframe = None
        self.loop = False

    def set_current_keyframe(self, idx):
        self.current_keyframe = self.keyframes[idx]

    def add_keyframe(self, obj):
        idx = len(self.keyframes)
        self.keyframes[idx] = KeyFrame.from_sprite(obj)


class AppScene(BaseScene):
    def setup(self):
        self.details = AnimationDetails()
        self.obj = SquareSprite(size=200, color=WHITE)
        self.obj.position = (300, 460)

        self.sprites = arcade.SpriteList()

        self.setup_ui()
        self.setup_tabs()
        self.setup_radio()

        self.drag_proxy = DragProxy(self.details)
        self.drag_proxy.current_attribute = 'position'

        self.events.drag(self.obj, self.drag_proxy)
        self.sprites.append(self.obj)

    def setup_ui(self):
        self.frame = SquareSprite(size=600, color=TEAL)
        self.frame.position = (300, 460)
        self.sprites.append(self.frame)

        self.loop_checkbox = SquareSprite(color=BRICK_RED, size=40)
        self.loop_checkbox.position = (155, 80)
        self.sprites.append(self.loop_checkbox)

        def init_button(text, handler, x, y):
            btn = Button(text=text, events=self.events)
            self.events.click(btn, handler)
            btn.position = (x, y)
            self.sprites.append(btn)

        init_button('+1 Frame', self.add_keyframe, 70, 130)
        init_button('Loop', self.toggle_loop, 70, 80)
        init_button('Play', self.play, 70, 30)
        init_button('Stop', self.stop, 193, 30)

    def setup_tabs(self):
        tab_names = ['Position', 'Angle', 'Scale', 'Width', 'Height']
        self.tabs = TabGroup(self.sprites, self.events, tab_names, 600,
                             (300, 740), 4)
        self.tabs['Position'].active = True

        def set_mouse_to_value(sprite, *args, **kwargs):
            self.drag_proxy.current_attribute = sprite.text.lower()

        for name in tab_names:
            self.events.click(self.tabs[name], set_mouse_to_value)

    def setup_radio(self):
        self.keyframes_radio = RadioGroup(self.sprites, self.events, [], 560,
                                          (405, 130), 10)
        self.add_keyframe()

    def add_keyframe(self, *args, **kwargs):
        idx = len(self.details.keyframes)
        if idx >= 5:
            return
        self.keyframes_radio.add_button(str(idx))
        self.keyframes_radio[str(idx)].on_click()
        self.details.add_keyframe(self.obj)
        self.events.click(self.keyframes_radio[str(idx)], self.select_keyframe)
        self.details.set_current_keyframe(
            int(self.keyframes_radio.active.text))

    def select_keyframe(self, *args, **kwargs):
        self.details.set_current_keyframe(
            int(self.keyframes_radio.active.text))
        seq = Sequence()
        seq.add_keyframe(0, self.details.current_keyframe)
        self.obj.animate(seq)

    def toggle_loop(self, *args, **kwargs):
        self.details.loop = not self.details.loop
        self.loop_checkbox.set_texture(int(self.details.loop))

    def play(self, *args, **kwargs):
        seq = Sequence(loop=self.details.loop)
        seq.add_keyframes(*self.details.keyframes.items())
        self.obj.animate(seq)

    def stop(self, *args, **kwargs):
        self.curtains.current_scene.animations.animations = []


class DragProxy:
    def __init__(self, details):
        self.current_attribute = None
        self.details = details

    def __call__(self, *args, **kwargs):
        getattr(self, self.current_attribute)(*args, **kwargs)

    def angle(self, sprite, x, y, dx, dy):
        dx = x - sprite.center_x
        dy = y - sprite.center_y
        sprite.angle = (math.atan2(dy, dx) * 180 / math.pi)
        self.details.current_keyframe.angle = sprite.angle

    def position(self, sprite, x, y, dx, dy):
        new_pos = (x, y)
        sprite.position = new_pos
        self.details.current_keyframe.position = sprite.position

    def scale(self, sprite, x, y, dx, dy):
        val = (x - (x + dx)) * 0.05
        sprite.scale = to_valid_bound(sprite.scale + val, 1, 2)
        self.details.current_keyframe.scale = sprite.scale

    def width(self, sprite, x, y, dx, dy):
        val = (x - (x + dx)) * 0.5
        sprite.width = to_valid_bound(sprite.width + val, 100, 400)
        self.details.current_keyframe.width = sprite.width

    def height(self, sprite, x, y, dx, dy):
        val = (y - (y + dy)) * 0.5
        sprite.height = to_valid_bound(sprite.height + val, 100, 400)
        self.details.current_keyframe.height = sprite.height


class Window(arcade.Window):
    def __init__(self):
        super().__init__(600, 760, 'move')
        self.curtains = Curtains(self)
        self.curtains.add_scenes({
            'scene': AppScene(),
        })
        self.curtains.set_scene('scene')


Window()
arcade.run()
