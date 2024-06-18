import pytest
from dataFormat import format

def test_format1():
    assert format('pixel_counts_export.csv') == 0

def test_format2():
    assert format('no_existe.csv') == 1

def test_format3():
    assert format('vacio.csv') == 2

def test_format4():
    assert format('pixelCount.py') == 3