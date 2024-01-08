from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class LoggerSetup :
    def __init__(self) :
        print('logger started')
        self.__logger = logging.getLogger()
        self.__logger.handlers = []
        self.__message_formatter = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'

    def set_logs_format(self, message_format:str) -> LoggerSetup :
        self.__message_formatter = message_format

        return self

    def set_info_logs(self) -> LoggerSetup :
        self.__logger.setLevel(logging.INFO)

        return self

    def set_debug_logs(self) -> LoggerSetup :
        self.__logger.setLevel(logging.DEBUG)

        return self

    def set_warning_logs(self) -> LoggerSetup :
        self.__logger.setLevel(logging.WARNING)

        return self

    def set_console_logs(self) -> LoggerSetup :
        logging_formatter = logging.Formatter(self.__message_formatter)
        logging_handler = logging.StreamHandler()

        logging_handler.setFormatter(logging_formatter)
        self.__logger.addHandler(logging_handler)

        return self

    def set_logs_timetable(self, logger_src:str='external\\logs', timetable:str='midnight',
                           duration:int=1, logs_copies:int=7) -> LoggerSetup :
        if not os.path.exists(logger_src) : os.makedirs(logger_src)

        logging_formatter = logging.Formatter(self.__message_formatter)
        time_marker = datetime.now().strftime('%d-%m-%Y')
        time_handler = TimedRotatingFileHandler(f'{logger_src}/eye_tracker_{time_marker}.log',
                                                when=timetable, interval=duration, backupCount=logs_copies)

        time_handler.setFormatter(logging_formatter)
        time_handler.suffix = '%d-%m-%Y'
        self.__logger.addHandler(time_handler)

        return self