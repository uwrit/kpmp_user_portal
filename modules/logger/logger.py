''' logging module '''
import os
import logging

def get_root_logger(name, filename=None):
    ''' get the logger '''
    logger = logging.getLogger(name)
    debug = os.environ.get('ENV', 'production') == 'development'
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if filename:
        fh = logging.FileHandler(filename)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def get_child_logger(root_logger, name):
    return logging.getLogger('.'.join([root_logger, name]))
