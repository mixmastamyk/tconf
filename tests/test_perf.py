'''
    tconf - TurtleConfig tests
'''
from timeit import timeit

from tconf import TurtleConfig

import config as AppDefaults


cfg = TurtleConfig(
    'AppyMcApp',
    sources = (
        './test.ini',
        './test.yaml',
        '{user_config_dir}/test.ini',
        AppDefaults,
    ),
)



r = timeit(
    "cfg['main.jpeg_quality']",
    number=100_000,
    globals=globals()
)

print('timeit:', r)
print('cache:', cfg._values_cache)  # about 20 times faster
