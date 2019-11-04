import arcade

from arcade_curtains import Curtains


class CircleSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textures = [
            arcade.make_soft_circle_texture(100, arcade.color.WHITE, 255, 255),
            arcade.make_soft_circle_texture(100, arcade.color.GREEN, 255, 255)
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
