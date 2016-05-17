import sys
import logging

def get_default_level():
    return get_debug_level()

def get_debug_level():
    return logging.DEBUG

def get_info_level():
    return logging.INFO

def get_logger(name, level=logging.INFO, formatting='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):    
    logger = logging.getLogger(name)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter(formatting)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(level)
    return logger
