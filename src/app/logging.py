import logging
import sys


def configure_logging(log_level: str) -> None:
    app_logger = logging.getLogger("app")
    if not any(handler.name == "app-console" for handler in app_logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.set_name("app-console")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        app_logger.addHandler(handler)
    app_logger.setLevel(log_level)
    app_logger.propagate = False
