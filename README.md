[![Build Status](https://travis-ci.com/maarten-dp/arcade-curtains.svg?branch=master)](https://travis-ci.com/maarten-dp/arcade-curtains)
[![Codecov](https://codecov.io/gh/maarten-dp/arcade-curtains/branch/master/graph/badge.svg)](https://codecov.io/gh/maarten-dp/arcade-curtains)
[![PyPI version](https://badge.fury.io/py/arcade-curtains.svg)](https://pypi.org/project/arcade-curtains/)

## Introduction

Arcade-curtains is a basic scene and event manager for [Arcade](https://github.com/pvcraven/arcade). The main goal is to provide a way to write event driven games instead of plastering your code with ifs and elses. This is achieved by writing handlers for events.

### Events

There are two types of events.

Sprite mouse events:
- `up`
- `down`
- `click`
- `hover`
- `out`
- `drag`

Global events:
- `frame`
- `before_draw`
- `after_draw`
- `key`

You can attach your event handlers on a per sprite basis. Meaning each sprite/event combination could have a unique handler.

### Scenes

Scenes are a way to pipe events to a certain context. You can define sprites and events in one scene, and they will become inactive when you enter another scene, for which you can define a whole new set of sprites and events. It also allows you to write some setup or teardown code when entering or leaving scenes.

When switching from one scene to another, the context and state of the previous scene is still retained. Meaning you can easily switch between scenes and continue where you previously had left off. A quick example would be accessing a menu or inventory in the middle of a level.

### Drawbacks

Eventhough this way of writing games allows for a more modular approach, ultimately leading to more readable code, it's easy to lose track of execution flow when debugging. Therefore it is advised to write your handlers to directly handle what you want to achieve instead of diverging into a number of different code paths based on the state of the game.

In addition to this, the library has not yet been benchmarked and so it's not known at what point the event handler gets saturated.

## Getting started

### Binding Curtains to Arcade

As the library itself is pretty basic, getting started is fairly easy.
The first thing you have to do is create an instance of the Curtains class, and bind it to your Arcade window.

```python
import arcade
from arcade_curtains import Curtains


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.curtains = Curtains(self)
```

or

```python
import arcade
from arcade_curtains import Curtains


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

curtains = Curtains()
window = Window()
curtains.bind(window)
```

When you bind the Curtains instance to an Arcade window, it will immediately bind itself to the window event methods (e.g. `update`, `on_draw`, `on_mouse_motion`). From then on, it will pipe the events to the event manager of the currently selected scene.

You are still able to overload these Arcade window methods as normal, but it is not advised to do so. If you do, know that the code written in these functions will be executed first, and Curtains handlers after.

### Creating a Scene

Scenes are the basis of this library, and when using curtains, every game needs at least one.

Once you've defined your Curtains instance, you can add a scene to it. But to be able to do this, you will have to subclass the `BaseScene` class provided by `arcade-curtains` and overload the setup method.
In the setup method you can run all code that is making sprites, spritelists and linking your handlers.

Anything subclassing `BaseScene` will auto detect `SpriteList` instances and auto draw on each frame.

```python
import arcade
from arcade_curtains import Curtains, BaseScene


class MyOpeningScene(BaseScene):
    def setup(self):
        # Actors will automatically be picked up and drawn on each frame
        self.actors = arcade.SpriteList()
        self.actor = arcade.Sprite()


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.curtains = Curtains(self)
        self.curtains.add_scene('opening_scene', MyOpeningScene())
        self.curtains.set_scene('opening_scene')
```

### Sprite events

Now that we've initialized curtains to have a scene, we can start adding events.

As explained above, there are two types of events. Unfortunately, these types are still a bit obfuscated at this point and are treated the same way, from a code point of view. The only difference is that for the sprite events, you need to give the sprite to the manager when registering a handler.

Sprite events usually occur when an interraction is being done with a specific sprite.
Let's create a scene with one actor and add a `hover`, `out` and `click` event.

```python
import arcade
from arcade_curtains import BaseScene

from .my_custom_sprites import CustomSprite


def paint_border(sprite, x, y):
    sprite.set_border_texture()


def unpain_border(sprite, x, y):
    sprite.unset_border_texture()


def kill_actor(sprite, x, y):
    sprite.play_death_animation(callback=sprite.kill)


class MyOpeningScene(BaseScene):
    def setup(self):
        self.actors = arcade.SpriteList()
        self.actor = CustomSprite()

        # add a hover event to this scene that paints a border whenever the mouse hovers over the sprite
        self.events.hover(self.actor, paint_border)
        # add an out event that reverts back to the original texture
        self.events.out(self.actor, unpain_border)
        # and one that kills the actor when clicked
        self.events.click(self.actor, kill_actor)
```

### Global events

Some events are not linkable to a sprite, but you would still like to define some handlers to it. For instance the `frame` event, which is triggered at every frame. You could treat it as a sprite event, but it wouldn't make sense as it doesn't get triggered due to sprite interaction. Instead, you can just attach a handler function, that interracts with the desired sprite, to the `frame` event.


```python
import arcade
from arcade_curtains import BaseScene


class CustomSprite(arcade.Sprite):
    def spin(self, delta_time):
        self.angle += delta_time
        self.angle %= 360


class MyOpeningScene(BaseScene):
    def setup(self):
        self.actors = arcade.SpriteList()
        self.actor = CustomSprite()

        self.events.frame(sprite.spin)
```

Alternatively you can add a handler that doesn't interract with a sprite in any way.

```python
import random

import arcade
from arcade_curtains import BaseScene

COLORS = [getattr(arcade.color, color) for color in dir(arcade.color)]


def trip_balls(delta):
    arcade.set_background_color(random.choice(COLORS))


class MyOpeningScene(BaseScene):
    def setup(self):
        self.events.frame(trip_balls)
```

Adding keyboard events is equally easy, and uses the arcade keymap to define handlers

```python
import sys

import arcade

from arcade_curtains import BaseScene


def exit(key):
    sys.exit(0)


class MyOpeningScene(BaseScene):
    def setup(self):
        self.events.key(arcade.key.ESCAPE, exit)
```


## Planned features

A planned addition to this library is an animation manager that is able to animate until a condition is met. (An example of how that would work can be found in `examples/theatre.py::MoveAnimator`).

The current Arcade animations are a bit black and white, meaning you have to manually turn it on or off. The animation manager would be a "fire and forget" principle. You could tell the sprite to move to a given location, or grow to a given scale, at a given speed, and you can trust the manager to take care of everything and cleaning up after the animation is done.
