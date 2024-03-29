import logging
from logging import config as _config

from common import globalvariable


LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": globalvariable.sysargs.debuglevel,
            "formatter": "simple",
            "class": "logging.StreamHandler"
        },
    },
    "loggers": {
        "gserver": {
            "handlers": ["console"],
            "level": "DEBUG"
        }
    }
}

_config.dictConfig(LOG_CONFIG)

# 日志
lgserver = logging.getLogger("gserver")
