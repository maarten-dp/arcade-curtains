from unittest.mock import Mock

import pytest


@pytest.fixture(scope='function')
def sprite():
    points = ((0, 0), (0, 100), (100, 0), (100, 100))
    return Mock(points=points)
