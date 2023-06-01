import operator as op
from unittest import mock

import pytest
import arcade

import arcade_curtains as c
from arcade_curtains.helpers import TriggerAttr, Widget

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


def test_it_can_observe_before_change():
    observable = c.helpers.ObservableSprite()
    handler = mock.Mock()
    observable.before_change('attr', handler)
    observable.attr = 10
    handler.assert_called_once()


def test_it_can_observe_after_change():
    observable = c.helpers.ObservableSprite()
    handler = mock.Mock()
    observable.after_change('attr', handler)
    observable.attr = 10
    handler.assert_called_once()


def test_it_can_observe_trigger_change():
    observable = c.helpers.ObservableSprite()
    handler = mock.Mock()
    health = TriggerAttr('health')
    observable.trigger(health > 10, handler)
    observable.health = 11
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
    assert anchor.position == (300, 300)
    assert sprite1.position == (350, 350)
    assert sprite2.position == (450, 450)


def test_it_can_make_anchor_from_sprite():
    sprite1 = arcade.Sprite()
    sprite1.position = (100, 100)
    anchor = c.helpers.AnchorPoint.from_sprite(sprite1, orientation='position')
    assert anchor.position == (100, 100)


def test_it_can_delay_setting_an_attribute(sprite):
    sprite.health = 10
    delayed = c.helpers.delay_set_attribute(sprite, "health", 20)
    assert sprite.health == 10
    delayed()
    assert sprite.health == 20


@pytest.mark.parametrize('op', [op.lt, op.gt, op.eq, op.le, op.ge, op.ne])
def test_it_can_build_a_trigger(sprite, op):
    health = TriggerAttr('health')
    trigger = op(health, 10)
    with pytest.raises(NotImplementedError):
        trigger.check(10)
    sprite.health = 10
    trigger.bake(sprite)
    assert isinstance(trigger.check(10), bool)


@mock.patch("arcade.get_window")
def test_it_can_get_widget_bounds(get_window):
    class MyWidget(Widget):
        def setup(self):
            pass

    get_window.return_value = mock.Mock(width=1000, height=800)
    wdg = MyWidget(x=200, y=300, width=100, height=150)

    assert wdg.position == (200, 300)
    assert wdg.topleft == (150, 425)
    assert wdg.topright == (750, 425)
    assert wdg.bottomleft == (150, 225)
    assert wdg.bottomright == (750, 225)
    assert wdg.bottom == 225
    assert wdg.top == 425
    assert wdg.left == 150
    assert wdg.right == 750


@mock.patch("arcade.get_window")
def test_it_can_set_widget_bounds(get_window):
    class MyWidget(Widget):
        def setup(self):
            pass

    get_window.return_value = mock.Mock(width=1000, height=800)
    wdg = MyWidget(x=200, y=300, width=100, height=150)

    wdg.left = 100
    assert wdg.right == 800

    wdg.right = 100
    assert wdg.left == 800

    wdg.top = 100
    assert wdg.bottom == 550

    wdg.bottom = 100
    assert wdg.top == 550
