import arcade

from arcade_curtains import Curtains, BaseScene, AnchorPoint

import math


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def move_anchor(sprite, x, y, dx, dy, anchor):
    anchor.position = (x, y)


class CircleSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        size = kwargs.pop('size', 100)
        super().__init__(*args, **kwargs)
        self.textures = [
            arcade.make_soft_circle_texture(size, arcade.color.WHITE, 255,
                                            255),
        ]
        self.texture = self.textures[0]


class Planet(CircleSprite):
    def revolve(self, delta):
        self.position = rotate(self.center.position, self.position, delta)


class SmallScene(BaseScene):
    def setup(self):
        self.sprites = arcade.SpriteList()
        self.center_of_the_universe = CircleSprite(size=150)
        self.center_of_the_universe.position = (250, 250)
        anchor = AnchorPoint.from_sprite(self.center_of_the_universe,
                                         'position')

        planets = 6
        rad = math.radians(360 / planets)
        for i in range(planets):
            planet = Planet(size=50)
            planet.center = self.center_of_the_universe
            planet.position = rotate((250, 250), (150, 150), i * rad)
            anchor.dock(planet)
            self.sprites.append(planet)
            self.events.frame(planet.revolve)

        self.events.drag(self.center_of_the_universe, move_anchor,
                         {'anchor': anchor})
        self.sprites.append(self.center_of_the_universe)


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, 'Anchor')
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
