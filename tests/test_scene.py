from unittest.mock import Mock

from arcade.application import MOUSE_BUTTON_LEFT
import pytest

from arcade_curtains import BaseScene, Curtains


class Scene(BaseScene):
    def setup(self):
        pass


@pytest.fixture(scope='function')
def curtains():
    window = Mock()
    curtains = Curtains(window)
    scene1 = Scene()
    scene2 = Scene()
    curtains.add_scenes({
        'scene1': scene1,
        'scene2': scene2,
    })
    curtains.set_scene('scene1')
    return curtains


def test_it_triggers_the_right_scene_event(sprite, curtains):
    scene1, scene2 = curtains.scenes.values()
    scene1.events.click(sprite, sprite.handler)
    scene2.events.click(sprite, sprite.handler)
    scene1.events.click(sprite, sprite.handler1)
    scene2.events.click(sprite, sprite.handler2)

    curtains.on_mouse_press(50, 50, MOUSE_BUTTON_LEFT, 0)
    curtains.on_mouse_release(50, 50, MOUSE_BUTTON_LEFT, 0)
    sprite.handler.assert_called_once()
    sprite.handler1.assert_called_once()

    curtains.set_scene('scene2')
    curtains.on_mouse_press(50, 50, MOUSE_BUTTON_LEFT, 0)
    curtains.on_mouse_release(50, 50, MOUSE_BUTTON_LEFT, 0)
    assert sprite.handler.call_count == 2
    sprite.handler2.assert_called_once()


def test_it_can_kill_a_sprite(sprite, curtains):
    def trigger():
        curtains.on_mouse_press(50, 50, MOUSE_BUTTON_LEFT, 0)
        curtains.on_mouse_release(50, 50, MOUSE_BUTTON_LEFT, 0)
        curtains.update(1)

    scene1 = curtains.scenes['scene1']
    scene1.events.down(sprite, sprite.handler)
    scene1.events.up(sprite, sprite.handler)
    scene1.events.frame(sprite.handler)
    trigger()

    assert sprite.handler.call_count == 3

    scene1.events.kill(sprite)

    trigger()
    assert sprite.handler.call_count == 3
    assert sprite not in scene1.events.all_sprites


def test_it_can_remove_a_sprite_handler(sprite, curtains):
    scene1 = curtains.scenes['scene1']
    scene1.events.down(sprite, sprite.handler)
    curtains.on_mouse_press(50, 50, MOUSE_BUTTON_LEFT, 0)

    assert sprite.handler.call_count == 1

    scene1.events.remove_down(sprite, sprite.handler)
    curtains.on_mouse_press(50, 50, MOUSE_BUTTON_LEFT, 0)

    assert sprite.handler.call_count == 1


def test_it_can_remove_a_handler(sprite, curtains):
    scene1 = curtains.scenes['scene1']
    scene1.events.frame(sprite.handler)
    curtains.update(1)

    assert sprite.handler.call_count == 1

    scene1.events.remove_frame(sprite.handler)
    curtains.update(1)

    assert sprite.handler.call_count == 1


def test_it_can_remove_a_handler_everywhere(sprite, curtains):
    scene1 = curtains.scenes['scene1']

    def trigger():
        scene1.events.trigger_before_draw()
        scene1.events.trigger_after_draw()
        curtains.update(1)

    scene1.events.before_draw(sprite.handler)
    scene1.events.after_draw(sprite.handler)
    scene1.events.frame(sprite.handler)
    trigger()

    assert sprite.handler.call_count == 3

    scene1.events.remove_from_all(sprite.handler)
    trigger()

    assert sprite.handler.call_count == 3
