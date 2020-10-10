from scipy.interpolate import interp1d
import numpy as np
import arcade
import attr

TRACKED_ATTRIBUTES = [
    'center_x',
    'center_y',
    'position',
    'angle',
    'scale',
    'width',
    'height',
    'alpha',
    'left',
    'right',
    'bottom',
    'top',
]


def interp2d(speed, points):
    x_points, y_points = zip(*points)
    fx = interp1d(speed, x_points)
    fy = interp1d(speed, y_points)

    def func(val):
        return (float(fx(val)), float(fy(val)))

    return func


def _valid(value):
    if isinstance(value, (list, tuple, set)):
        return not all([np.isnan(a) for a in value])
    return not np.isnan(value)


class NoActiveSceneException(Exception):
    pass


class AnimationManager:
    def __init__(self):
        self.animations = []

    def fire(self, sprite, sequence):
        if isinstance(sequence, Sequence):
            animator = Animator(sprite, sequence)
        elif isinstance(sequence, Chain):
            animator = sequence
        else:
            raise ValueError('Cannot fire {}'.format(
                sequence.__class__.__name__))
        self.animations.append(animator)

    def _blip(self, delta):
        for animator in self.animations[:]:
            animator.blip(delta)
            if animator.finished:
                self.animations.remove(animator)

    def kill(self, sprite):
        for animator in self.animations[:]:
            if animator.kill(sprite):
                self.animations.remove(animator)


class AnimationManagerProxy:
    def __init__(self, sprite):
        self.sprite = sprite

    def __call__(self, sequence=None, manager=None, **kwargs):
        if isinstance(sequence, KeyFrame):
            sequence = self._sequence_from_keyframe(sequence, **kwargs)
        if not sequence and kwargs:
            sequence = self._sequence_from_kwargs(**kwargs)
        self._get_manager(manager).fire(self.sprite, sequence)

    def kill(self):
        curtains = arcade.get_window().curtains
        for scene in curtains.scenes.values():
            scene.animations.kill(self.sprite)

    def _sequence_from_kwargs(self, **kwargs):
        callback = kwargs.pop('callback', None)
        duration = kwargs.pop('duration', 1)
        loop = kwargs.pop('loop', False)
        sequence = Sequence(loop=loop)
        sequence.add_keyframe(
            keyframe=KeyFrame.from_sprite(self.sprite, kwargs.keys()))
        sequence.add_keyframe(duration, KeyFrame(**kwargs))

        if callback:
            sequence.add_callback(duration, callback)
        return sequence

    def _sequence_from_keyframe(self, keyframe, **kwargs):
        kwargs.update(keyframe.to_dict())
        return self._sequence_from_kwargs(**kwargs)

    def _get_manager(self, manager=None):
        if manager is None:
            curtains = arcade.get_window().curtains
            if not curtains.current_scene:
                msg = 'use curtains.set_scene before animating a sprite'
                raise NoActiveSceneException(msg)
            manager = curtains.current_scene.animations
        return manager


class SequenceIndex:
    def __init__(self, sequence, index):
        self.sequence = sequence
        self.index = index

    @property
    def frame(self):
        return self.sequence.keyframes.get(self.index)

    @frame.setter
    def frame(self, value):
        self.sequence.add_keyframe(self.index, value)

    @property
    def callback(self):
        return self.sequence.callbacks.get(self.index)

    @callback.setter
    def callback(self, value):
        self.sequence.add_callback(self.index, value)


@attr.s
class Sequence:
    default_interval = attr.ib(default=1)
    keyframes = attr.ib(attr.Factory(dict))
    callbacks = attr.ib(attr.Factory(dict))
    is_reversed = attr.ib(default=False)
    loop = attr.ib(default=False)

    def __iter__(self):
        return iter(self.keyframes.items())

    def __getitem__(self, key):
        return SequenceIndex(self, key)

    def __len__(self):
        return len(self.keyframes)

    def _sort(self, collection):
        for key in sorted(collection.keys()):
            collection[key] = collection.pop(key)

    def _clean_point_in_time(self, pit):
        if not pit:
            default = [-1 * self.default_interval]
            pit = (list(self.keyframes.keys())
                   or default)[-1] + self.default_interval
        return pit

    def add_keyframe(self,
                     point_in_time=None,
                     keyframe=None,
                     callback=None,
                     **kwargs):
        point_in_time = self._clean_point_in_time(point_in_time)
        if not keyframe and kwargs:
            keyframe = KeyFrame(**kwargs)
        self.keyframes[point_in_time] = keyframe
        if callback:
            self.callbacks[point_in_time] = callback
        self._sort(self.keyframes)
        self._sort(self.callbacks)

    def add_keyframes(self, *keyframes):
        for keyframe in keyframes:
            if isinstance(keyframe, dict):
                self.add_keyframe(**keyframe)
            else:
                self.add_keyframe(*keyframe)

    def add_callback(self, point_in_time, callback):
        self.callbacks[point_in_time] = callback
        self._sort(self.callbacks)

    @property
    def total_time(self):
        return list(self.keyframes.keys())[-1]

    def _to_point_in_times(self):
        duration = list(self.keyframes.keys())
        if len(duration) == 1:
            duration.append(duration[0] + 0.0001)
        all_points = list(zip(*[k.to_list() for k in self.keyframes.values()]))
        pits = {}
        interp_fn = {'position': interp2d}

        attributes = TRACKED_ATTRIBUTES
        for idx, attribute in enumerate(attributes):
            points = all_points[idx]
            if len(points) == 1:
                points = points * 2
            if self.is_reversed:
                points = list(reversed(points))

            include = [_valid(p) for p in points]
            if not any(include):
                continue

            fn = interp_fn.get(attribute, interp1d)

            pit = PointInTime(fn(duration, points), self.total_time)
            pits[attribute] = pit
        return pits

    @classmethod
    def from_sprite(cls, sprite):
        sequence = cls()
        sequence.add_keyframe(0, KeyFrame.from_sprite(sprite))
        return sequence


@attr.s
class KeyFrame:
    center_x = attr.ib(default=np.nan)
    center_y = attr.ib(default=np.nan)
    position = attr.ib(default=np.nan)
    angle = attr.ib(default=np.nan)
    scale = attr.ib(default=np.nan)
    width = attr.ib(default=np.nan)
    height = attr.ib(default=np.nan)
    alpha = attr.ib(default=np.nan)
    top = attr.ib(default=np.nan)
    bottom = attr.ib(default=np.nan)
    left = attr.ib(default=np.nan)
    right = attr.ib(default=np.nan)

    @classmethod
    def from_sprite(cls, sprite, only_keys=None):
        if not only_keys:
            only_keys = ['position', 'angle', 'width', 'height']
        kwargs = {}
        for key in only_keys:
            kwargs[key] = getattr(sprite, key)
        return cls(**kwargs)

    def to_list(self):
        return [getattr(self, attr) for attr in TRACKED_ATTRIBUTES]

    def to_dict(self):
        result = {}
        for key in TRACKED_ATTRIBUTES:
            value = getattr(self, key)
            if _valid(value):
                result[key] = value
        return result


class Animator:
    def __init__(self, sprite, sequence):
        self.sprite = sprite
        self.loop = sequence.loop
        self._elapsed_time = 0
        self._total_time = sequence.total_time
        self.pits = sequence._to_point_in_times()
        self.callbacks = iter(sequence.callbacks.items())
        self.upcoming_callback()

    def upcoming_callback(self):
        try:
            self._upcoming_callback = next(self.callbacks)
        except StopIteration:
            self._upcoming_callback = None

    def blip(self, delta):
        self._elapsed_time += delta
        for attrib, pit in self.pits.items():
            value = pit.point_at(self._elapsed_time)
            if _valid(value):
                setattr(self.sprite, attrib, value)

        self.check_for_callback()

        if self.finished:
            if self.loop:
                self._elapsed_time = 0

    def kill(self, sprite):
        if sprite is self.sprite:
            return True
        return False

    def check_for_callback(self):
        if not self._upcoming_callback:
            return
        time, callback = self._upcoming_callback
        if time <= self._elapsed_time:
            self.upcoming_callback()
            callback()

    @property
    def finished(self):
        return self._elapsed_time >= self._total_time

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @property
    def remaining_time(self):
        return self._total_time - self._elapsed_time


class PointInTime:
    def __init__(self, fn, duration):
        self.fn = fn
        self.duration = duration

    def point_at(self, time):
        if time > self.duration:
            time = self.duration
        return self.fn(time)


class Chain:
    def __init__(self, loop=False, callback=None):
        self.loop = loop
        self.animations = []
        self.anim_queue = None
        self.current_animator = None
        self.finished = False
        self.callback = callback

    def add_sequences(self, *anims):
        for anim in anims:
            self.add_sequence(*anim)

    def add_sequence(self, *anim):
        self.animations.append(anim)

    def blip(self, delta):
        if not self.anim_queue:
            self.anim_queue = iter(self.animations)
            self._next_animator()

        if self.finished:
            return

        self.current_animator.blip(delta)
        if self.current_animator.finished:
            anim = self.current_animator
            mod = anim.elapsed_time - anim._total_time
            self._next_animator()
            self.current_animator.blip(mod)

    def kill(self, sprite):
        if self.anim_queue is None:
            return False

        if self.current_animator.sprite is sprite:
            return True

        anim_queue = []
        for anim_sprite, sequence in self.anim_queue:
            anim_queue.append((anim_sprite, sequence))
            if sprite is anim_sprite:
                return True
        self.anim_queue = iter(anim_queue)

        return False

    def _next_animator(self):
        try:
            sprite, sequence = next(self.anim_queue)
            animator = Animator(sprite, sequence)
            self.current_animator = animator
        except StopIteration:
            if self.callback:
                self.callback()
            if self.loop and self.animations:
                self.anim_queue = None
            else:
                self.finished = True
