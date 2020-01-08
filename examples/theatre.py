import arcade
from scipy.interpolate import interp1d

from arcade_curtains import Curtains
from arcade_curtains.scene import BaseScene

SCREEN_WIDTH = 620
SCREEN_HEIGHT = 260
SCREEN_TITLE = "Play"
PADDING = 20

WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
GREEN = arcade.color.GREEN
RED = arcade.color.RED


class BasicSprite(arcade.Sprite):
    texture_maker = None

    def __init__(self, *args, **kwargs):
        color = kwargs.pop('color', BLACK)
        self.size = kwargs.pop('size', 100)

        super().__init__(*args, **kwargs)
        self.texture = self.get_texture(self.size, color)
        self.textures = [
            self.texture,
            self.get_texture(self.size, GREEN),
            self.get_texture(self.size, RED),
        ]

    def get_texture(self, size, color):
        raise NotImplementedError()


class SquareSprite(BasicSprite):
    def get_texture(self, size, color):
        return arcade.make_soft_square_texture(size, color, 255, 255)


class CircleSprite(BasicSprite):
    def get_texture(self, size, color):
        return arcade.make_soft_circle_texture(size, color, 255, 255)

    def green(self, *args):
        self.set_texture(1)

    def black(self, *args):
        self.set_texture(0)


class MoveAnimator:
    def __init__(self, sprite, x, y, events):
        self.speed = .1
        self.sprite = sprite
        self.elapsed_time = 0
        self.events = events

        x_points = [sprite.center_x, x]
        y_points = [sprite.center_y, y]
        self.x_path = interp1d([0, self.speed], x_points)
        self.y_path = interp1d([0, self.speed], y_points)

        self.events.frame(self.move)

    def move(self, delta):
        self.elapsed_time += delta
        if self.elapsed_time > self.speed:
            self.elapsed_time = self.speed
            # The animation has ended, remove it from the event handler
            self.events.remove_frame(self.move)

        self.sprite.center_x = float(self.x_path(self.elapsed_time))
        self.sprite.center_y = float(self.y_path(self.elapsed_time))


class CharacterDevelopment(BaseScene):
    next_scene = 'scene2'
    primary_color = WHITE
    secondary_color = BLACK

    def setup(self):
        # set up button drawer
        self.labels = []
        self.buttons = arcade.SpriteList()
        self.actors = arcade.SpriteList()

        # set up buttons
        btn_add_actor = SquareSprite(
            center_x=60, center_y=60, color=self.secondary_color)
        btn_next_scene = SquareSprite(
            center_x=180, center_y=60, color=self.secondary_color)
        self.buttons.append(btn_add_actor)
        self.buttons.append(btn_next_scene)

        # set up button events
        self.events.click(btn_next_scene,
                          lambda *x: self.curtains.set_scene(self.next_scene))
        self.events.click(btn_add_actor, self.add_actor)

        self.add_label(btn_add_actor, "Add\nActor", self.primary_color)
        self.add_label(btn_next_scene, "Next\nScene", self.primary_color)

    def add_label(self, attach_to, text, color):
        x = attach_to.center_x - (attach_to.width / 2) + 10
        y = attach_to.center_y

        def draw_label(*args, **kwargs):
            arcade.draw_text(text, x, y, color, 14)

        self.events.after_draw(draw_label)

    def enter_scene(self, previous_scene):
        arcade.set_background_color(self.primary_color)

    def add_actor(self, sprite, x, y):
        actor = CircleSprite(color=self.secondary_color)
        x = SCREEN_WIDTH / 2
        y = SCREEN_HEIGHT - (actor.height / 2) - PADDING
        if len(self.actors):
            neighbour = self.actors.sprite_list[-1]
            x = neighbour.center_x + actor.width + PADDING
        actor.center_x = x
        actor.center_y = y
        self.actors.append(actor)

        self.events.hover(actor, actor.green)
        self.events.out(actor, actor.black)

        if len(self.actors) == 1:
            return

        if len(self.actors) == 5:
            # We don't want any more actors, the stage is getting too crowded
            self.events.remove_click(sprite, self.add_actor)
            sprite.set_texture(2)

        # Ass some nice animations
        offset = (actor.width + PADDING) / 2
        for actor in self.actors:
            MoveAnimator(actor, actor.center_x - offset, actor.center_y,
                         self.events)


class PlotTwist(CharacterDevelopment):
    next_scene = 'scene3'
    previous_scene = 'scene1'
    primary_color = BLACK
    secondary_color = WHITE

    def setup(self):
        super().setup()
        btn_previous_scene = SquareSprite(
            center_x=300, center_y=60, color=self.secondary_color)
        self.events.click(
            btn_previous_scene,
            lambda *x: self.curtains.set_scene(self.previous_scene))
        self.buttons.append(btn_previous_scene)

        self.add_label(btn_previous_scene, "Previous\nScene",
                       self.primary_color)


class DeusExMachina(BaseScene):
    def setup(self):
        self.buttons = arcade.SpriteList()
        btn_scene1 = SquareSprite(center_x=60, center_y=60)
        btn_scene2 = SquareSprite(center_x=180, center_y=60)
        self.events.click(btn_scene1,
                          lambda *x: self.curtains.set_scene('scene1'))
        self.events.click(btn_scene2,
                          lambda *x: self.curtains.set_scene('scene2'))
        self.buttons.append(btn_scene1)
        self.buttons.append(btn_scene2)

        self.add_label(btn_scene1, "Go To\nScene1", WHITE)
        self.add_label(btn_scene2, "Go To\nScene2", WHITE)

    def enter_scene(self, previous_scene):
        arcade.set_background_color(GREEN)

    add_label = CharacterDevelopment.add_label


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.curtains = Curtains(self)
        self.curtains.add_scenes({
            'scene1': CharacterDevelopment(),
            'scene2': PlotTwist(),
            'scene3': DeusExMachina()
        })

    def setup(self):
        self.curtains.set_scene('scene1')


if __name__ == "__main__":
    window = Window()
    window.setup()
    try:
        arcade.run()
    except KeyboardInterrupt:
        pass
