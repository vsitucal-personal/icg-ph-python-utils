import logging
import sys
import os

from icgphutils import Constants


class Logger:
    logger = None
    logger_name = None
    handler = None

    @classmethod
    def get_logger(
        cls,
        log_level=os.getenv('LOG_LEVEL', "DEBUG"),
        logger_name='ICGPHLogger',
        propagate_log=False,
    ):
        if not cls.logger:
            logger = logging.getLogger(logger_name)
            handler = logging.StreamHandler(sys.stdout)

            log_format = '[%(asctime)s][%(module)s][%(funcName)s][%(levelname)s]: %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'

            log_formatter = logging.Formatter(log_format, datefmt=date_format)
            handler.setFormatter(log_formatter)

            logger.propagate = propagate_log
            logger.addHandler(handler)
            logger.setLevel(log_level)

            cls.logger_name = logger_name
            cls.logger = logger
            cls.handler = handler

        return cls.logger

    @classmethod
    def destroy_logger(cls):
        if cls.logger:
            cls.handler.flush()
            cls.handler.close()
            root_logger = logging.getLogger(cls.logger_name)
            for handle in root_logger.handlers:
                handle.close()
                root_logger.removeHandler(handle)
            cls.logger = None
            cls.logger_name = None


class FormatMessage(object):
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args, **self.kwargs)
