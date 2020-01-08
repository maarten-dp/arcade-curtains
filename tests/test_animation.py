from arcade_curtains import animation as a
import arcade
import numpy as np
from unittest import mock


def sprite_instance():
    s = arcade.Sprite()
    s.center_x = 10
    s.center_y = 20
    s.position = (10, 20)
    s.angle = 50
    s.width = 100
    s.height = 200
    s.scale = 1
    return s


def test_it_can_interp2d():
    points = ([0, 0], [5, 10], [20, 40])
    f = a.interp2d([0, 1, 2], points)
    assert f(.5) == (2.5, 5.)
    assert f(1.5) == (12.5, 25.)


def test_it_can_patch_arcade_sprite():
    assert isinstance(arcade.Sprite().animate, a.AnimationManagerProxy)


def test_it_can_patch_subclassed_arcade_sprite():
    class SomeSubClass(arcade.Sprite):
        pass

    assert isinstance(SomeSubClass().animate, a.AnimationManagerProxy)


def test_it_can_give_a_correcT_point_in_time():
    pit = a.PointInTime(a.interp1d([0, 1], [0, 10]), 1)
    assert pit.point_at(.1) == 1
    assert pit.point_at(1) == 10
    assert pit.point_at(10) == 10


def test_it_can_make_a_keyframe_from_sprite():
    s = sprite_instance()
    k = a.KeyFrame.from_sprite(s)
    assert k.to_dict() == {
        'position': (10, 20),
        'angle': 50,
        'width': 100,
        'height': 200,
    }


def test_it_can_make_a_keyframe_from_sprite_with_target_keys():
    s = sprite_instance()
    k = a.KeyFrame.from_sprite(s, only_keys=['center_x', 'center_y', 'scale'])
    assert k.to_dict() == {
        'center_x': 10,
        'center_y': 20,
        'scale': 1,
    }


def test_it_can_transform_a_keyframe_to_list():
    s = sprite_instance()
    k = a.KeyFrame.from_sprite(s)
    expected = [np.nan, np.nan, (10, 20), 50, np.nan, 100, 200]
    assert k.to_list() == expected


def test_it_can_add_a_keyframe_to_a_sequence():
    s = a.Sequence()
    k = a.KeyFrame()
    s.add_keyframe(0, k)
    assert id(s[0]) == id(k)


def test_it_can_add_a_keyframes_to_a_sequence():
    s = a.Sequence()
    k1 = a.KeyFrame()
    k2 = a.KeyFrame()
    some_callback = lambda: 1
    s.add_keyframes((0, k1), (1, k2, some_callback))
    assert id(s[0]) == id(k1)
    assert id(s[1]) == id(k2)
    assert s.callbacks[1] == some_callback


def test_it_can_make_a_sequence_from_a_sprite():
    s = a.Sequence().from_sprite(sprite_instance())
    assert len(s) == 1
    assert s[0].position == (10, 20)


def test_it_can_generate_points_in_time_from_a_sequence():
    s = a.Sequence()
    k1 = a.KeyFrame(position=(10, 10), angle=0, height=100)
    k2 = a.KeyFrame(position=(10, 100), angle=100, height=200)
    s.add_keyframes((0, k1), (1, k2))
    pits = s._to_point_in_times()
    assert len(pits) == 3
    assert list(pits.keys()) == ['position', 'angle', 'height']
    assert pits['position'].point_at(.5) == (10, 55)
    assert pits['angle'].point_at(.5) == 50
    assert pits['height'].point_at(.5) == 150
    assert pits['height'].point_at(1) == 200
    assert pits['height'].point_at(10) == 200


def test_it_can_animate_a_sprite_over_time():
    s = a.Sequence()
    k1 = a.KeyFrame(position=(10, 10), angle=0, height=100)
    k2 = a.KeyFrame(position=(10, 100), angle=100, height=200)
    s.add_keyframes((0, k1), (1, k2))
    inst = sprite_instance()

    anim = a.Animator(inst, s)
    anim.blip(.5)
    assert inst.position == (10, 55)
    assert not anim.finished
    anim.blip(1)
    assert inst.position == (10, 100)
    assert anim.finished


def test_it_can_execute_a_callback_at_a_given_time():
    s = a.Sequence()
    k1 = a.KeyFrame(position=(10, 10))
    k2 = a.KeyFrame(position=(10, 100))
    s.add_keyframes((0, k1), (1, k2))
    callback = mock.Mock().some_callback
    s.add_callback(.5, callback)
    inst = sprite_instance()
    anim = a.Animator(inst, s)
    anim.blip(.4)
    callback.assert_not_called()
    anim.blip(.2)
    callback.assert_called_once()
    anim.blip(.4)
    callback.assert_called_once()
    assert not anim._upcoming_callback


def test_it_can_make_a_sequence_from_kwargs():
    proxy = a.AnimationManagerProxy(arcade.Sprite())
    seq = proxy._sequence_from_kwargs(
        position=(100, 400), duration=10, callback=lambda: None, loop=True)
    assert seq.loop
    assert seq.total_time == 10
    assert seq.callbacks[10]
    assert len(seq) == 2
    assert seq[10].position == (100, 400)


def test_it_can_make_a_sequence_from_keyframe():
    proxy = a.AnimationManagerProxy(arcade.Sprite())
    seq = proxy._sequence_from_keyframe(
        a.KeyFrame(position=(100, 400)),
        duration=10,
        callback=lambda: None,
        loop=True)
    assert seq.loop
    assert seq.total_time == 10
    assert seq.callbacks[10]
    assert len(seq) == 2
    assert seq[10].position == (100, 400)


@mock.patch('arcade_curtains.animation.AnimationManagerProxy._get_manager')
def test_it_can_fire_an_animation(mngr):
    manager = mock.Mock()
    mngr.return_value = manager
    proxy = a.AnimationManagerProxy(arcade.Sprite())
    proxy(position=(100, 400), )
    manager.fire.assert_called_once()


def test_it_can_play_animations():
    s = a.Sequence()
    k1 = a.KeyFrame(position=(10, 10))
    k2 = a.KeyFrame(position=(10, 100))
    s.add_keyframes((0, k1), (1, k2))
    inst = arcade.Sprite()
    manager = a.AnimationManager()
    manager.fire(inst, s)
    assert len(manager.animations) == 1
    manager._blip(.5)
    assert len(manager.animations) == 1
    assert inst.position == (10, 55)
    manager._blip(2)
    assert len(manager.animations) == 0
    assert inst.position == (10, 100)


def test_it_can_chain_animations():
    def make_sequence():
        s = a.Sequence()
        k1 = a.KeyFrame(position=(10, 10))
        k2 = a.KeyFrame(position=(10, 100))
        s.add_keyframes((0, k1), (1, k2))
        return s

    seq1 = make_sequence()
    seq2 = make_sequence()
    inst1 = arcade.Sprite()
    inst2 = arcade.Sprite()
    chain = a.Chain()
    chain.add_sequence(inst1, seq1)
    chain.add_sequence(inst2, seq2)
    chain.blip(0)
    assert inst1.position == (10, 10)
    assert inst2.position == (0, 0)
    chain.blip(.5)
    assert inst1.position == (10, 55)
    assert inst2.position == (0, 0)
    chain.blip(1)
    assert inst1.position == (10, 100)
    assert inst2.position == (10, 55)
    chain.blip(1)
    assert inst1.position == (10, 100)
    assert inst2.position == (10, 100)
    assert chain.finished
