import logging
import re
import sys

from app.infrastructure.config.settings import settings

_RTSP_PATTERN = re.compile(r"(rtsp://[^:]+:)[^@]+(@)", re.IGNORECASE)


class RtspCredentialFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.getMessage and isinstance(record.msg, str):
            record.msg = _RTSP_PATTERN.sub(r"\1****\2", record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: _RTSP_PATTERN.sub(r"\1****\2", v) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    _RTSP_PATTERN.sub(r"\1****\2", a) if isinstance(a, str) else a
                    for a in record.args
                )
        return True


def setup_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    root.addFilter(RtspCredentialFilter())

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
