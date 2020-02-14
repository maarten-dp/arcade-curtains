import arcade
import random

from arcade_curtains import (Curtains, BaseScene, ObservableSprite, KeyFrame,
                             Sequence, Widget)
from arcade_curtains.helpers import delay_set_attribute, TriggerAttr
from example_helpers import SquareSprite, Button, CircleSprite

STATE = None


# State management
def get_state():
    global STATE
    if STATE is None:
        STATE = State()
    return STATE


class State:
    IDLE = 1
    WAITING = 2

    def __init__(self):
        self.current_state = self.IDLE
        self.handlers = []

    def __eq__(self, other):
        return self.current_state == other

    def set_waiting(self):
        self.current_state = self.WAITING

    def set_idle(self):
        self.current_state = self.IDLE

    def update(self, delta):
        if self == State.WAITING:
            return
        for handler in self.handlers:
            handler(delta)

    def add_handler(self, handler):
        self.handlers.append(handler)


# function to allow readability
def play_animation(args):
    sprite, seq = args
    sprite.animate(seq)


# animation maker functions
def powerup(sprite):
    flash = SquareSprite()
    flash.color = arcade.color.GOLD
    flash.position = sprite.position

    target = (sprite.center_x, sprite.center_y + 100)
    seq = Sequence()
    seq[0].frame = KeyFrame.from_sprite(sprite, ['position', 'scale', 'alpha'])
    seq[1].frame = KeyFrame(position=target, scale=1.5, alpha=0)
    seq[1].callback = flash.kill

    arcade.get_window().curtains.current_scene.flash_sprites.append(flash)
    return flash, seq


def attack(sprite):
    x = sprite.center_x
    opx = sprite.opponent.center_x

    seq = Sequence()

    seq[0].frame = KeyFrame.from_sprite(sprite, ['center_x', 'height'])
    seq[.2].frame = KeyFrame(center_x=x - 20, height=sprite.height)
    seq[.3].frame = KeyFrame(center_x=opx, height=sprite.height - 30)
    seq[.31].frame = KeyFrame(center_x=opx, height=sprite.height)
    seq[.8].frame = seq[0].frame

    seq[.3].callback = sprite.opponent.take_damage
    seq[.31].callback = delay_set_attribute(sprite, 'special',
                                            sprite.special + 20)
    seq[.8].callback = delay_set_attribute(sprite, 'stamina', 0)

    return sprite, seq


def takedmg(sprite):
    c = arcade.color
    sprite.color = c.RED

    seq = Sequence()

    seq[0].frame = KeyFrame.from_sprite(sprite, ['center_x'])
    seq[.1].frame = KeyFrame(center_x=sprite.center_x + 30)
    seq[.2].frame = KeyFrame(center_x=sprite.center_x - 10)
    seq[.3].frame = seq[0].frame

    seq[.1].callback = delay_set_attribute(sprite, 'color', sprite.skin_color)
    return sprite, seq


def powerup_generator(sprite):
    rate = sprite.flash_rate
    time = sprite.power_up_time
    flashes = []
    for i in range(int(time / rate)):
        flashes.append(powerup(sprite))

    def make_fn(flash):
        def fn():
            play_animation(flash)

        return fn

    amount = len(flashes)
    for i, (_, seq) in enumerate(flashes):
        if i + 1 < amount:
            seq[rate].callback = make_fn(flashes[i + 1])
        else:
            seq[.99].callback = sprite.attack
    return flashes[0]


class CharacterPortrait(Widget):
    def setup_widget(self, inverse=False):
        c = arcade.color
        bars = [('health', c.RED), ('stamina', c.BLUE), ('special', c.GREEN)]
        self.bars = {}

        for idx, (bar_name, color) in enumerate(reversed(bars)):
            container = Bar(arcade.color.WHITE, height=23, width=103)
            bar = Bar(color, inverse=inverse)
            bar.topleft = (50, idx * 25)
            container.position = bar.position
            self.sprites.extend([container, bar])
            self.bars[bar_name] = bar

        topleft = 0
        if inverse:
            topleft = 121

        padding = CircleSprite(size=80, color=c.SADDLE_BROWN)
        padding.topleft = (topleft, 55)

        portrait = CircleSprite(size=70, color=c.PERU)
        portrait.topleft = (topleft + 5, 50)

        backdrop = SquareSprite()
        backdrop.color = c.SADDLE_BROWN
        backdrop.width = 108
        backdrop.height = 85
        backdrop.position = self.bars['stamina'].position
        backdropleft = CircleSprite(size=85, color=c.SADDLE_BROWN)
        backdropleft.position = (backdrop.left, backdrop.center_y)
        backdropright = CircleSprite(size=85, color=c.SADDLE_BROWN)
        backdropright.position = (backdrop.right, backdrop.center_y)

        for sprite in [backdrop, backdropright, backdropleft]:
            self.sprites.insert(0, sprite)

        self.sprites.extend([padding, portrait])


class Menu(Widget):
    def setup_widget(self, events, hero):
        backdrop = SquareSprite()
        backdrop.color = arcade.color.SADDLE_BROWN
        backdrop.width = 245
        backdrop.height = 95
        backdrop.bottomleft = (0, 0)

        attack = Button(text='Attack', events=events)
        haste = Button(text='Haste', events=events)
        ultimate = Button(text='Ultimate', events=events)
        self.sprites.extend([backdrop, attack, ultimate, haste])

        events.click(attack, hero.attack)
        events.click(ultimate, hero.power_up)
        events.click(haste, hero.haste)

        attack.bottomleft = (5, 50)
        haste.bottomleft = (125, 50)
        ultimate.bottomleft = (5, 5)

        self._sequences = {}
        for sprite in self.sprites:
            sprite.alpha = 0

    @property
    def sequences(self):
        if not self._sequences:
            for sprite in self.sprites:
                seq = Sequence()
                seq[0].frame = KeyFrame.from_sprite(
                    sprite, ['width', 'height', 'position'])
                seq[0].frame.alpha = 255
                seq[.2].frame = KeyFrame(
                    width=0, height=0, position=self.anchor.position, alpha=0)
                self._sequences[sprite] = seq
        return self._sequences

    def show(self):
        for sprite, seq in self.sequences.items():
            seq.is_reversed = True
            sprite.animate(seq)

    def hide(self):
        for sprite, seq in self.sequences.items():
            seq.is_reversed = False
            sprite.animate(seq)


class Ambience(Widget):
    def setup_widget(self, events):
        arcade.set_background_color(arcade.color.SKY_BLUE)

        grass = SquareSprite()
        grass.color = arcade.color.FOREST_GREEN
        grass.width = 500
        grass.height = 200
        grass.bottomleft = (0, 0)
        self.sprites.append(grass)

        class GrassBlade(SquareSprite):
            def __init__(self):
                self.wind = random.random() / 2
                super().__init__()

            def blow_in_the_wind(self, delta):
                self.wind += delta
                if self.wind > 3:
                    self.wind = 0
                elif self.wind > 2.6:
                    self.angle -= delta * 100
                    self.center_x += delta * 10
                elif self.wind > 2.2:
                    self.angle += delta * 100
                    self.center_x -= delta * 10
                elif self.wind > 1.8:
                    self.angle -= delta * 100
                    self.center_x += delta * 10
                elif self.wind > 1.4:
                    self.angle += delta * 100
                    self.center_x -= delta * 10

        for i in range(1100):
            grassblade = GrassBlade()
            grassblade.color = (14, 119, 14)
            grassblade.width = 2
            grassblade.height = 10
            grassblade.bottomleft = (random.randint(0, 500),
                                     random.randint(0, 200))
            self.sprites.append(grassblade)
            events.frame(grassblade.blow_in_the_wind)

        class Cloud(Widget):
            def setup_widget(self):
                base = CircleSprite()
                base.width = 256
                base.height = 64
                base.position = (0, 0)

                top1 = CircleSprite()
                top1.position = (88, 30)

                top2 = CircleSprite()
                top2.scale = 1.3
                top2.position = (20, 50)

                top3 = CircleSprite()
                top3.scale = 0.9
                top3.position = (-50, 20)

                self.sprites.extend([top1, top2, top3, base])
                self.speed = random.randint(50, 100)

            def move(self, delta):
                self.center_x -= delta * self.speed
                if self.center_x < -150:
                    self.center_x = 700

        cloud1 = Cloud()
        cloud1.position = (random.randint(128, 372), 300)
        self.sprites.extend(cloud1.sprites)

        cloud2 = Cloud()
        cloud2.position = (random.randint(128, 372), 400)
        self.sprites.extend(cloud2.sprites)

        cloud3 = Cloud()
        cloud3.position = (random.randint(128, 372), 500)
        self.sprites.extend(cloud3.sprites)

        events.frame(cloud1.move)
        events.frame(cloud2.move)
        events.frame(cloud3.move)


class Controller:
    def __init__(self, char, input_device, scene, inverse):
        self.char = char
        self.input_device = input_device

        portrait = CharacterPortrait(inverse=inverse)
        portrait.position = self.char.position
        portrait.center_y += 240
        portrait.register(scene.sprites)

        self.char.after_change('health', portrait.bars['health'].set_value)
        self.char.after_change('stamina', portrait.bars['stamina'].set_value)
        self.char.after_change('special', portrait.bars['special'].set_value)
        get_state().add_handler(self.char.update)
        char.special = 0

        stamina = TriggerAttr('stamina')
        self.char.trigger(stamina >= 100, self.get_input)
        self.char.trigger(stamina == 0, self.cleanup)

        health = TriggerAttr('health')
        self.char.trigger(health == 0, char.die)

    def get_input(self):
        get_state().set_waiting()
        self.input_device.get_input()

    def cleanup(self):
        get_state().set_idle()
        self.input_device.cleanup()


class Character(SquareSprite, ObservableSprite):
    def __init__(self, name, rate=.02, *args, **kwargs):
        ObservableSprite.__init__(self, *args, **kwargs)
        SquareSprite.__init__(self, *args, **kwargs)
        self.skin_color = arcade.color.PERU
        self.color = self.skin_color
        self.name = name

        self.health = 100
        self.stamina = 0
        self.special = 0
        self.flash_rate = 0.15
        self.power_up_time = 1
        self.opponent = None

        self.recovery_rate = rate
        self.current_recovery_time = 0

        self.damage = 12.5

        self.state = get_state()

    def update(self, delta):
        if self.stamina < 100:
            self.current_recovery_time += delta
            if self.current_recovery_time > self.recovery_rate:
                stam = int(self.current_recovery_time / self.recovery_rate)
                self.current_recovery_time = self.current_recovery_time % self.recovery_rate
                self.stamina += stam

    def power_up(self, *args, **kwargs):
        if self.special < 100:
            return
        play_animation(powerup_generator(self))
        self.special = 0

    def die(self):
        self.kill()
        if self.name == 'hero':
            arcade.get_window().curtains.set_scene('defeat')
        else:
            arcade.get_window().curtains.set_scene('victory')

    def haste(self, *args, **kwargs):
        self.recovery_rate /= 2
        self.stamina = 0

    def attack(self, *args, **kwargs):
        if self.stamina < 100:
            return

        play_animation(attack(self))

    def take_damage(self, *args, **kwargs):
        play_animation(takedmg(self))
        self.health -= self.opponent.damage


class Bar(SquareSprite):
    def __init__(self,
                 color,
                 height=20,
                 width=100,
                 inverse=False,
                 *args,
                 **kwargs):
        SquareSprite.__init__(self, *args, **kwargs)
        self.width = width
        self.height = height
        self.color = color
        self.orientation = 'right' if inverse else 'left'

    def set_perc(self, perc):
        if perc > 1:
            perc = 1
        if perc < 0:
            perc = 0

        orig = getattr(self, self.orientation)
        self.width = 100 * perc
        setattr(self, self.orientation, orig)

    def set_value(self, sprite, attr, old, new):
        if new == 0:
            self.set_perc(0)
        else:
            self.set_perc(new / 100)


class PlayerInput:
    def __init__(self, char, menu):
        self.char = char
        self.menu = menu

    def get_input(self):
        self.menu.show()

    def cleanup(self):
        self.menu.hide()


class AIInput:
    def __init__(self, char):
        self.char = char

    def get_input(self):
        if self.char.special == 100:
            self.char.power_up()
        else:
            self.char.attack()

    def cleanup(self):
        pass


class SmallScene(BaseScene):
    def setup(self):
        self.flash_sprites = arcade.SpriteList()
        self.sprites = arcade.SpriteList()

        ambience = Ambience(events=self.events)
        ambience.bottomleft = (0, 0)
        ambience.register(self.sprites)

        self.hero = Character(name='hero', rate=.019)
        self.hero.position = (100, 200)
        self.villain = Character(name='villain')
        self.villain.position = (400, 200)
        self.hero.opponent = self.villain
        self.villain.opponent = self.hero

        self.sprites.append(self.hero)
        self.sprites.append(self.villain)

        menu = Menu(events=self.events, hero=self.hero)
        menu.register(self.sprites)
        menu.bottomleft = (5, 5)

        Controller(self.hero, PlayerInput(self.hero, menu), self, False)
        Controller(self.villain, AIInput(self.villain), self, True)


class ResultScene(BaseScene):
    def setup(self, message, color):
        self.message = message
        self.color = color
        self.events.after_draw(self.display_message)
        self.alpha = 0

    def enter_scene(self, prev_scene):
        arcade.set_background_color(arcade.color.BLACK)

    def display_message(self):
        self.alpha += 5
        if self.alpha > 255:
            self.alpha = 255
        arcade.draw_text(
            self.message,
            250,
            250,
            self.color + (self.alpha, ),
            35,
            align="center",
            anchor_x="center",
            anchor_y="center")


class Window(arcade.Window):
    def __init__(self):
        super().__init__(500, 500, 'move')
        self.curtains = Curtains(self)
        self.dispatcher = get_state()
        self.curtains.add_scene('scene1', SmallScene())
        self.curtains.add_scene(
            'victory',
            ResultScene(message='You Win :)', color=arcade.color.GREEN))
        self.curtains.add_scene(
            'defeat', ResultScene(
                message='You Lose :(', color=arcade.color.RED))

    def setup(self):
        self.curtains.set_scene('scene1')

    def update(self, delta):
        self.dispatcher.update(delta)


def run(window):
    window.setup()
    try:
        arcade.run()
    except KeyboardInterrupt:
        pass


run(Window())
