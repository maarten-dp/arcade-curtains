import arcade

from arcade_curtains import Curtains
from PIL import Image, ImageFont, ImageDraw

WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
GREEN = arcade.color.GREEN
BRICK_RED = arcade.color.BRICK_RED
TEAL = arcade.color.TEAL
ROYAL_PURPLE = arcade.color.ROYAL_PURPLE
CORNFLOWER_BLUE = arcade.color.CORNFLOWER_BLUE


class BasicSprite(arcade.Sprite):
    texture_maker = None

    def __init__(self, *args, **kwargs):
        color = kwargs.pop('color', WHITE)
        self.size = kwargs.pop('size', 100)

        super().__init__(*args, **kwargs)
        self.texture = self.get_texture(self.size, color)
        self.textures = [
            self.texture,
            self.get_texture(self.size, TEAL),
            self.get_texture(self.size, CORNFLOWER_BLUE),
        ]

    def get_texture(self, size, color):
        raise NotImplementedError()


class SquareSprite(BasicSprite):
    def get_texture(self, size, color):
        return arcade.make_soft_square_texture(size, color, 255, 255)


class Button(SquareSprite):
    default_width = 115
    default_height = 40

    def __init__(self, text, events, *args, **kwargs):
        self.text = text
        self.button_height = kwargs.get('button_height', self.default_height)
        self.button_width = kwargs.get('button_width', self.default_width)

        events.hover(self, self.on_hover)
        events.out(self, self.on_out)
        events.down(self, self.down)
        events.up(self, self.up)

        super().__init__(*args, **kwargs)

    def get_texture(self, size, color):
        font = ImageFont.truetype("FreeMonoBold", 20)
        img = Image.new("RGBA", (self.button_width, self.button_height), color)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), self.text, font=font, align="left", fill=BLACK)
        name = '{}:{}:{}'.format('btn', color, self.text)
        return arcade.Texture(name, img)

    def on_hover(self, *args, **kwargs):
        self.set_texture(1)

    def on_out(self, *args, **kwargs):
        self.set_texture(0)

    def down(self, *args, **kwargs):
        self.set_texture(2)

    def up(self, *args, **kwargs):
        self.set_texture(1)


class ButtonGroup:
    button_class = None

    def __init__(self, spritelist, events, buttons, width, position, padding):
        self.buttons = {}
        self.spritelist = spritelist
        self.x, self.y = position
        self.padding = padding
        self.events = events
        self.tab_width = self.button_class.default_width
        self.start_x = (self.x - (width / 2)) + (self.tab_width / 2) + padding
        self.active = None

        for text in buttons:
            self.add_button(text)

    def add_button(self, text):
        btn = self.button_class(text=text, group=self, events=self.events)
        btn.center_x = self.start_x + (
            (self.tab_width + self.padding) * len(self.buttons))
        btn.center_y = self.y
        self.buttons[text] = btn
        self.spritelist.append(btn)

    def __iter__(self):
        return iter(self.buttons.values())

    def __getitem__(self, key):
        return self.buttons[key]


class TabButton(Button):
    def __init__(self, group, *args, **kwargs):
        self._active = False
        self.group = group
        super().__init__(*args, **kwargs)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.on_out()

    def on_out(self, *args, **kwargs):
        if self.active:
            self.set_texture(1)
        else:
            self.set_texture(0)

    def on_click(self, *args, **kwargs):
        self.group.active = self
        for btn in self.group:
            btn.active = btn == self


class RadioButton(Button):
    default_width = 40
    border_width = 7

    def __init__(self, group, *args, **kwargs):
        self.group = group
        super().__init__(*args, **kwargs)

    def on_click(self, *args, **kwargs):
        try:
            self.group.selected_border.animate(
                position=self.position,
                width=self.width + self.border_width,
                height=self.height + self.border_width,
                duration=.1)
        except Exception:
            self.group.selected_border.position = self.position
            self.group.selected_border.width = self.width + self.border_width
            self.group.selected_border.height = self.height + self.border_width
        self.group.active = self


class RadioGroup(ButtonGroup):
    button_class = RadioButton

    def __init__(self, spritelist, *args, **kwargs):
        self.selected_border = SquareSprite(color=BRICK_RED)
        spritelist.append(self.selected_border)
        super().__init__(spritelist, *args, **kwargs)


class TabGroup(ButtonGroup):
    button_class = TabButton


class CircleSprite(arcade.Sprite):
    def __init__(self, color=arcade.color.WHITE, size=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textures = [
            arcade.make_soft_circle_texture(size, color, 255, 255),
            arcade.make_soft_circle_texture(size, arcade.color.GREEN, 255, 255)
        ]
        self.texture = self.textures[0]
        self.center_x = 70
        self.center_y = 70

    def toggle_texture(self, *args, **kwargs):
        self.set_texture(int(not self.textures.index(self.texture)))


def get_window(name, Scene):
    class Window(arcade.Window):
        def __init__(self):
            super().__init__(140, 140, name)
            self.curtains = Curtains(self)
            self.curtains.add_scene('scene1', Scene())

        def setup(self):
            self.curtains.set_scene('scene1')

    return Window()


def run(window):
    window.setup()
    try:
        arcade.run()
    except KeyboardInterrupt:
        pass
