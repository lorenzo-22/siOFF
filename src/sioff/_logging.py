import sys


def setup_logging(verbose: bool) -> None:
    # Imported here, not at module top: loguru costs ~0.4 s that `sioff --help`
    # (which never logs) should not pay.
    from loguru import logger

    logger.remove()
    if verbose:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        )
    else:
        logger.add(sys.stderr, level="WARNING", format="<level>{message}</level>")
