import pytest
import arcade_curtains as c
import arcade
from unittest import mock

orientations = {
    'topleft': (450, 725),
    'topright': (550, 725),
    'bottomleft': (450, 575),
    'bottomright': (550, 575)
}


@pytest.mark.parametrize('attr,expected', orientations.items())
def test_it_can_give_other_orientations(attr, expected):
    sprite = arcade.Sprite(center_x=500, center_y=650)
    sprite.width = 100
    sprite.height = 150
    assert getattr(sprite, attr) == expected


orientations = {
    'topleft': (450, 725),
    'topright': (550, 725),
    'bottomleft': (450, 575),
    'bottomright': (550, 575)
}


@pytest.mark.parametrize('attr,value', orientations.items())
def test_it_can_set_other_orientations(attr, value):
    sprite = arcade.Sprite()
    sprite.width = 100
    sprite.height = 150
    setattr(sprite, attr, value)
    assert sprite.position == (500, 650)


def test_it_can_observe_a_change():
    observable = c.helpers.ObservableSprite()
    handler = mock.Mock()
    observable.after_change('attr', handler)
    observable.attr = 10
    handler.assert_called_once()


def test_it_can_anchor_sprites():
    anchor = c.helpers.AnchorPoint(50, 50)
    sprite1 = arcade.Sprite()
    sprite1.position = (100, 100)
    sprite2 = arcade.Sprite()
    sprite2.position = (200, 200)

    anchor.dock(sprite1)
    anchor.dock(sprite2)

    anchor.position = (300, 300)
    assert sprite1.position == (350, 350)
    assert sprite2.position == (450, 450)
