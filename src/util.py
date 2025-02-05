from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")


def get_logger():
    return logger