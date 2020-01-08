import arcade

from arcade_curtains import Curtains, BaseScene, Sequence, KeyFrame, Chain


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
        self.actor1 = CircleSprite()
        self.actor2 = CircleSprite()
        self.actor2.position = (70, 430)
        self.sprites.append(self.actor1)
        self.sprites.append(self.actor2)

    def enter_scene(self, previous_scene):
        left1 = KeyFrame(position=self.actor1.position)
        left2 = KeyFrame(position=self.actor2.position)
        right1 = KeyFrame(position=(430, 70))
        right2 = KeyFrame(position=(430, 430))
        sequence1 = Sequence()
        sequence2 = Sequence()

        sequence1.add_keyframes((0, left1), (.5, right1), (1, left1))
        sequence2.add_keyframes((0, left2), (.5, right2), (1, left2))

        chain = Chain(loop=True)
        chain.add_sequences((self.actor1, sequence1), (self.actor2, sequence2))
        self.animations.fire(None, chain)


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
