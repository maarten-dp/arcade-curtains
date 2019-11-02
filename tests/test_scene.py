from unittest.mock import Mock

from arcade.application import MOUSE_BUTTON_LEFT

from arcade_curtains import BaseScene, Curtains


class Scene(BaseScene):
    def setup(self):
        pass


def test_it_triggers_the_right_scene_event(sprite):
    window = Mock()
    curtains = Curtains(window)
    scene1 = Scene(window)
    scene2 = Scene(window)
    curtains.add_scenes({
        'scene1': scene1,
        'scene2': scene2,
    })
    curtains.set_scene('scene1')

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
