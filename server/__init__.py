import logging

from server.config import LOG_FILE_PATH, LOG_LEVEL

logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_FILE_PATH,
)
