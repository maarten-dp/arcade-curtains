from unittest.mock import Mock

import pytest

ESCAPE = 65307


@pytest.mark.parametrize("event,triggers", [
    ('down', [('trigger_down', (50, 50))]),
    ('up', [('trigger_up', (50, 50))]),
    ('click', [('trigger_down', (50, 50)), ('trigger_up', (50, 50))]),
    ('hover', [('update', (50, 50)), ('update', (50, 50))]),
    ('out', [('update', (50, 50)), ('update', (-50, -50))]),
    ('drag', [('trigger_down', (50, 50)), ('trigger_drag', (50, 50, 1, 1))]),
])
def test_it_can_fire_sprite_events(sprite, event, triggers):
    from arcade_curtains.event import EventHandler
    ev = EventHandler()
    getattr(ev, event)(sprite, sprite.handler)
    for trigger, coords in triggers:
        getattr(ev, trigger)(*coords)
    sprite.handler.assert_called_once()


@pytest.mark.parametrize("event,triggers", [
    ('frame', [('trigger_frame', (50, ))]),
    ('before_draw', [('trigger_before_draw', ())]),
    ('after_draw', [('trigger_after_draw', ())]),
])
def test_it_can_fire_events(sprite, event, triggers):
    from arcade_curtains.event import EventHandler
    ev = EventHandler()
    getattr(ev, event)(sprite.handler)
    for trigger, args in triggers:
        getattr(ev, trigger)(*args)
    sprite.handler.assert_called_once()


def test_it_can_fire_keyboard_events(sprite):
    from arcade_curtains.event import EventHandler
    ev = EventHandler()
    ev.key(ESCAPE, sprite.handler)
    ev.trigger_key_press(ESCAPE)
    sprite.handler.assert_called_once()