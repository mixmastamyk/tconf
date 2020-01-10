'''
    tconf - TurtleConfig tests

    How to use a module instead of a class for the app defaults:
'''
import os
import sys

import out
from tconf import TurtleConfig, TurtleArgumentParser

import config as AppDefaults  # 👀


out.configure(level='debug' if '-d' in sys.argv else 'info')
if len(sys.argv) > 1:
    sys.argv.pop()  # :-O  hack


cfg = TurtleConfig(
    'AppyMcApp',
    sources = (
        TurtleArgumentParser(AppDefaults),
        os.environ,
        './test.ini',
        './test.yaml',
        #~ '{site_config_dir}/test.ini',
        '{user_config_dir}/test.ini',
        AppDefaults,
    ),
    ensure_paths=True,
)


#~ parser = TurtleArgumentParser(tcfg)
print()
# parse and validate
#~ args = parser.parse_args()

val = cfg['a_simple_option']
print('a_simple_option:', val, type(val))
assert val == False
print()

val = cfg['main.jpeg_quality']
print('quality:', val, type(val))
assert val == 96
print()

val = cfg['main.sync_dates_to_filesystem']
print('sync_dates:', val, type(val))
assert val == False
print()

val = cfg['sort.specific.name']
print('name:', val, type(val))
assert val == 'BoatyMcBoatface'
print()

