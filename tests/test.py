'''
    | tconf - TurtleConfig tests
    | © 2020, Mike Miller - Released under the LGPL, version 3+.
'''
import os, sys
import out  # this script requires the out package

from tconf import TurtleConfig

out.configure(level='debug' if '-d' in sys.argv else 'info')


class AppDefaults:

    # simple
    an_option = True
    a_null = None

    # hierarchy
    class main:
        jpeg_quality: int = 95
        # sync_dates_to_filesystem: tristate = True
        sync_dates_to_filesystem = True
        work_in_place = False
        dict_annotation: dict(type=int, desc='percentage') = 95
        foo = 'bar'

    class rotate:
        resample = 'BICUBIC'

    class sort:
        template = 'x y z'

        class specific:
            name = 'BoatyMcBoatface'


# tests
line = '-' * 70
app_name = 'AppyMcApp'


# default class only ------------------------------------------------------
cfg = TurtleConfig(app_name, sources=(AppDefaults,))

# simple
assert cfg.an_option is True
print(line)
assert cfg['an_option'] is True
print(line)

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)


# hierarchy
assert cfg.main.jpeg_quality == 95
print(line)
assert cfg['main.jpeg_quality'] == 95
print(line)

assert cfg.main.does_not_exist is None
print(line)
caught = False
try:
    assert cfg['main.does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)


caught = False
try:
    assert cfg.does_not_exist.does_not_exist
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)
#~ assert cfg['does_not_exist.does_not_exist'] is None
#~ print(line)

assert cfg.sort.specific.name == 'BoatyMcBoatface'
print(line)
assert cfg['sort.specific.name'] == 'BoatyMcBoatface'
print(line)


# environment only --------------------------------------------------------
cfg = TurtleConfig(app_name, sources=(os.environ, AppDefaults))

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)

# override with env var
os.environ['PY_APPYMCAPP.AN_OPTION'] = 'False'
assert cfg.an_option == False
print(line)
assert cfg['an_option'] == False
print(line)


#~ caught = False
#~ try:
assert cfg.main.jpeg_quality == 95
#~ except AttributeError:
    #~ caught = True
#~ assert caught
print(line)
assert cfg['main.jpeg_quality'] == 95
print(line)


# not able to work hierarchically unless full path given during access
os.environ['PY_APPYMCAPP.MAIN.JPEG_QUALITY'] = '94'
del cfg._values_cache['main.jpeg_quality']  # clear cache: important!

caught = False
try:
    assert cfg.main.jpeg_quality == 94  # doesn't work  :-(
except AssertionError:
    caught = True
assert caught
assert cfg['main.jpeg_quality'] == 94  # does work  :-)
print(line)


# ini only ----------------------------------------------------------------
cfg = TurtleConfig(app_name, sources=('./test.ini', AppDefaults))

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)

#~ assert cfg.main.does_not_exist == None
#~ assert cfg['main.does_not_exist'] == None
#~ print(line)

caught = False
try:
    assert cfg.does_not_exist.does_not_exist == None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)
#~ assert cfg['does_not_exist.does_not_exist'] == None
print(line)

assert cfg.main.jpeg_quality == 96
assert cfg['main.jpeg_quality'] == 96
assert cfg.jpeg_quality == 96  # look in main by default
print(line)


# json only ----------------------------------------------------------------
cfg = TurtleConfig(app_name, sources=('./test.json', AppDefaults))

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)

#~ assert cfg.main.does_not_exist == None
#~ assert cfg['main.does_not_exist'] == None
#~ print(line)

assert cfg.main.jpeg_quality == 96
print(line)
assert cfg['main.jpeg_quality'] == 96
print(line)
#~ assert cfg.jpeg_quality == None
#~ print(line)

# single
assert cfg.an_option == True
print(line)


# yaml only ----------------------------------------------------------------
cfg = TurtleConfig(app_name, sources=('./test.yaml', AppDefaults))

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)

#~ assert cfg.main.does_not_exist == None
#~ print(line)
#~ assert cfg['main.does_not_exist'] == None
#~ print(line)

assert cfg.main.jpeg_quality == 96
print(line)
assert cfg['main.jpeg_quality'] == 96
print(line)
#~ assert cfg.jpeg_quality == None
#~ print(line)

# single
assert cfg.an_option == True

assert cfg.a_null == None
print(line)


# xml only ----------------------------------------------------------------
cfg = TurtleConfig(app_name, sources=('./test.xml', AppDefaults))

caught = False
try:
    assert cfg.does_not_exist is None
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

caught = False
try:
    assert cfg['does_not_exist'] is None
except KeyError: # None has no attributes
    caught = True
assert caught
print(line)

assert cfg.main.jpeg_quality == 96
print(line)
assert cfg['main.jpeg_quality'] == 96
#~ assert cfg['main.jpeg_quality._unit'] == "percent"  # doesn't work yet
print(line)
#~ assert cfg.jpeg_quality == None
#~ print(line)

# single
assert cfg.an_option == True
#~ assert cfg.a_null2 == None
print(line)
assert cfg['sort.specific.name'] == 'BoatyMcBoatface'
print(line)


# all ---------------------------------------------------------------------
cfg = TurtleConfig(
    'AppyMcApp',
    sources = (
        os.environ,
        './test.ini',
        './test.yaml',
        '{site_config_dir}/test.ini',
        '{user_config_dir}/test.ini',
        AppDefaults,
    ),
    ensure_paths=True,
)

# from first
assert cfg.main.jpeg_quality == 96
print(line)

# from second
os.environ['PY_APPYMCAPP.AN_OPTION'] = 'False'
assert cfg.an_option == False
print(line)

# from third
caught = False
try:
    assert cfg.sort.specific.name == 'BoatyMcBoatface'
except AttributeError: # None has no attributes
    caught = True
assert caught
print(line)

assert cfg['sort.specific.name'] == 'BoatyMcBoatface'
print(line)
#~ assert cfg.a_null == None
print(line)
