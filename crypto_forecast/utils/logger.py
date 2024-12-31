import os
import logging

from pathlib import Path

# globals
FILE = Path(__file__).resolve() 
ROOT = FILE.parents[1]

LOGGER_FORMAT = logging.Formatter(
    "[%(asctime)s][%(name)s][%(levelname)s] >>> %(message)s"
)


def setup_logger(name, file_name, level=logging.INFO):
    """
    로거 객체 생성

    parameter
    ----------
    name(str): logger의 이름
    file_name(str): log 파일 명
    level(int): logger 정보 레벨

    return
    ----------
    logger(logging.getLogger): file과 console에 대한 logging을 수행하는 logger 객체

    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger
    
    # file handler
    file_handler = logging.FileHandler(os.path.join(ROOT, 'logs', file_name))
    file_handler.setLevel(level)
    file_handler.setFormatter(LOGGER_FORMAT)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(LOGGER_FORMAT)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

