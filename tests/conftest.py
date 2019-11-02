import sys
from unittest.mock import Mock, patch

import pytest

sys.modules['pyglet.gl'] = Mock()


@pytest.fixture(scope='function')
def sprite():
    points = ((0, 0), (0, 100), (100, 0), (100, 100))
    return Mock(points=points)


@pytest.fixture(scope='session', autouse=True)
def create_directories(request):
    with patch('arcade.application'):
        yield
