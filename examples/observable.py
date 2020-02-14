import arcade
import example_helpers as eh
from arcade_curtains import ObservableSprite
from arcade_curtains.helpers import TriggerAttr


class CircleSprite(eh.CircleSprite, ObservableSprite):
    pass


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, 'move')
        self.mod = 1
        self.sprites = arcade.SpriteList()
        self.sprite1 = CircleSprite()
        self.sprite1.position = (100, 100)
        self.sprite2 = CircleSprite()
        self.sprite2.position = (100, 400)
        self.sprites.append(self.sprite1)
        self.sprites.append(self.sprite2)

        def keep_pace(sprite, attribute, old, new):
            setattr(self.sprite2, attribute, new)

        def set_mod(mod):
            self.mod = mod

        center_x = TriggerAttr('center_x')
        self.sprite1.trigger(center_x > 400, lambda: set_mod(-1))
        self.sprite1.trigger(center_x < 100, lambda: set_mod(1))
        self.sprite1.after_change('center_x', keep_pace)

    def on_update(self, delta):
        arcade.start_render()
        self.sprite1.center_x += (delta * 100) * self.mod
        self.sprites.draw()


window = Window()
arcade.run()
