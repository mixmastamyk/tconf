# appy.py
from tconf import TurtleConfig, TurtleArgumentParser # 👀

import config as AppDefaults


tcfg = TurtleConfig(
    'AppyMcApp',
    sources = (
        TurtleArgumentParser(AppDefaults),  # 👀
        # environment, config files, etc…
        AppDefaults,
    ),
    ensure_paths=True,
)
