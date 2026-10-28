import logging
import sys

from app.logging import configure_logging


def test_writes_application_logs_as_text_to_stdout(capsys):
    configure_logging("INFO")

    logging.getLogger("app.main").info("Application started")

    output = capsys.readouterr()
    assert "INFO app.main: Application started" in output.out
    assert output.err == ""


def test_repeated_setup_does_not_duplicate_logs(capsys):
    configure_logging("INFO")
    configure_logging("INFO")

    logging.getLogger("app.main").info("Application started")

    assert len(capsys.readouterr().out.splitlines()) == 1


def test_does_not_reconfigure_root_or_library_loggers():
    root = logging.getLogger()
    previous_handlers = root.handlers.copy()
    previous_level = root.level
    library = logging.getLogger("httpx2")
    previous_library_level = library.level

    configure_logging("INFO")

    assert root.handlers == previous_handlers
    assert root.level == previous_level
    assert library.level == previous_library_level
    handler = next(
        handler
        for handler in logging.getLogger("app").handlers
        if handler.name == "app-console"
    )
    assert handler.stream is sys.stdout


def test_filters_messages_below_configured_level(log_threshold, capsys):
    level, expected = log_threshold
    configure_logging(level)
    logger = logging.getLogger("app.main")

    for name in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        logger.log(logging.getLevelNamesMapping()[name], name)

    lines = capsys.readouterr().out.splitlines()
    assert [line.rsplit(": ", 1)[-1] for line in lines] == expected


def test_repeated_setup_can_change_level_without_duplicate_handlers(capsys):
    configure_logging("INFO")
    configure_logging("ERROR")
    logger = logging.getLogger("app.main")

    logger.info("Should be filtered")
    logger.error("Request failed")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1
    assert "ERROR app.main: Request failed" in lines[0]
