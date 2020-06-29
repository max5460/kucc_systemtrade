import logging
from logging import config
from datetime import datetime
from CommonConstant import LOGFILE_STORE_FOLDER_NAME


def CreateLogger():
    logOutputFileName = LOGFILE_STORE_FOLDER_NAME + '//' + datetime.now().strftime('%Y%m%d') + '.log'
    formatter = '%(asctime)s\t%(module)s.%(funcName)s\t%(levelname)s\t%(message)s'
    standardFormatterName = 'standardFormatter'

    LOGGING = {
               'version': 1,
               'formatters': {
                              standardFormatterName: {
                                                      'class': 'logging.Formatter',
                                                      'format': formatter
                                                     }
                             },
               'handlers': {
                            'console': {
                                        'class': 'logging.StreamHandler',
                                        'level': 'DEBUG',
                                        'formatter': standardFormatterName
                                       },
                            'fileout': {
                                        'class': 'logging.handlers.RotatingFileHandler',
                                        'filename': logOutputFileName,
                                        'mode': 'a',
                                        'formatter': standardFormatterName,
                                        'encoding': 'utf-8'
                                       }
                           },
               'loggers': {
                           'standardLogger': {
                                              'handlers': ['console', 'fileout'],
                                              'propagate': 0,
                                              'level': 'DEBUG'
                                             }
                          },
               'root': {
                        'handlers': ['console', 'fileout'],
                        'level': 'DEBUG',
                        'disable_existing_loggers': False
                       },
              }

    logging.config.dictConfig(LOGGING)
