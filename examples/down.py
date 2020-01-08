import arcade
from example_helpers import CircleSprite, get_window, run

from arcade_curtains import BaseScene


class SmallScene(BaseScene):
    def setup(self):
        self.sprites = arcade.SpriteList()
        self.actor = CircleSprite()
        self.sprites.append(self.actor)

        handler_function = self.actor.toggle_texture
        self.events.down(self.actor, handler_function)


window = get_window('down_example', SmallScene)
run(window)
