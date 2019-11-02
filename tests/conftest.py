import sys
from unittest.mock import Mock, patch

import pytest

# Hard mocking pyglet.gl to account for the travis CI machines not having GLU
sys.modules['pyglet.gl'] = Mock()


@pytest.fixture(scope='function')
def sprite():
    points = ((0, 0), (0, 100), (100, 0), (100, 100))
    return Mock(points=points)
