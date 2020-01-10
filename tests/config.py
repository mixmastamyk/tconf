'''
    | tconf - TurtleConfig tests
    | © 2020, Mike Miller - Released under the LGPL, version 3+.

    How to use a module instead of a class:
'''
from typing import Tuple as _Tuple
from typing import Sequence as _Sequence
#~ from typing import Iterable as _Iterable
from typing import List as _List
from typing import Union as _Union


# simple
a_simple_option = False


# hierarchy
class main:
    jpeg_quality: dict(type=int, desc='the jpeg quality level') = 95
    sync_dates_to_filesystem = True
    work_in_place: bool = False


class rotate:
    resample: dict(
                type=str,
                desc='the resample method',
                choices=('BICUBIC', '2', '3'),
                # help=SUPPRESS,
              ) = 'BICUBIC'

class sort:
    template = 'x y z'

    class specific:
        name = 'BoatyMcBoatface'


class sequences:

    list_of_strings: _List[str] = ['one', 'two', 'three']

    tuple_of_strings: _Tuple[str, str, str] = ('one', 'two', 'three')

    sequence_of_stuff: _Sequence[_Union[str, int]] = ('one', 2, 'three')

    # Kaboom!
    #~ sequence_of_stuff: _Sequence[_Union[str, int]] = ('one', 2, None)
