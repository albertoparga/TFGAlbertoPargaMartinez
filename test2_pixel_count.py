import pytest
from pixelCount import init, getCount

def test_init2():
    assert init('ee-abcd') != 0

def test_getCount2():
    init('ee-abcd')
    assert getCount() != 0