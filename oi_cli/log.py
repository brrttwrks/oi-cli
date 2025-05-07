from pathlib import Path
import logging
import logging.config
import structlog
from .settings import *

log_path = OI_CLI_DIR / "oi_cli.log"

logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "stream": {
                "level": log_level,
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": log_level,
                "class": "logging.handlers.WatchedFileHandler",
                "filename": log_path,
            },
        },
        "loggers": {
            "": {
                "handlers": ["stream", "file"],
                "level": "DEBUG",
                "propagate": True,
            },
        }
})
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.EventRenamer("msg"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
    logger_factory=structlog.stdlib.LoggerFactory(),
)
log = structlog.get_logger(module="main")
