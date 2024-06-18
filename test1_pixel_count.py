import pytest
from pixelCount import auth, init, getCount

def test_init1():
    assert init('ee-albertopargamartinez') == 0

def test_getCount1():
    init('ee-albertopargamartinez')
    assert getCount() == 0