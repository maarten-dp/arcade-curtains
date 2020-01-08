import arcade

from arcade_curtains import Curtains, BaseScene


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


class SmallScene(BaseScene):
    def setup(self):
        self.sprites = arcade.SpriteList()
        self.actor = CircleSprite()

    def enter_scene(self, previous_scene):
        def callback():
            self.actor.animate(duration=.5, position=(70, 70), loop=True)

        self.actor.animate(position=(430, 430), duration=.5, callback=callback)
        self.sprites.append(self.actor)


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, 'move')
        self.curtains = Curtains(self)
        self.curtains.add_scene('scene1', SmallScene())

    def setup(self):
        self.curtains.set_scene('scene1')


def run(window):
    window.setup()
    try:
        arcade.run()
    except KeyboardInterrupt:
        pass


run(Window())
