'''
    | tconf - TurtleConfig tests
    | © 2020, Mike Miller - Released under the LGPL, version 3+.
'''

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

from tconf import TurtleConfig
import config as AppDefaults

import sys, out  # this script needs the out package
out.configure(level='debug' if '-d' in sys.argv else 'info')


cfg = TurtleConfig(
    'AppyMcApp',
    sources = (
        './test.ini',
        AppDefaults,
    ),
)


result = cfg['sequences.list_of_strings']
print('result:', repr(result), type(result))
assert type(result) is list


result = cfg['sequences.tuple_of_strings']
print('result:', repr(result), type(result))
assert type(result) is tuple


result = cfg['sequences.sequence_of_stuff']
print('result:', repr(result), type(result))
assert isinstance(result, Sequence)
