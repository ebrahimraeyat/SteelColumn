import sys
from pathlib import Path


FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)

import FreeCAD


steel_column = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(steel_column))

import columnTypeFunctions

def test_decompose_section_name():
    n, size, flang_plate, web_plate, side_plate, pa_baz = columnTypeFunctions.decompose_section_name('2IPE14FPL120X8WPL100X6SPL200X6CC')
    assert n == 2
    assert size == 14
    assert flang_plate == [120, 8]
    assert web_plate == [100, 6]
    assert side_plate == [200, 6]
    assert pa_baz



if __name__ == '__main__':
    test_decompose_section_name()