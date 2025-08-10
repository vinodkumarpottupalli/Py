import os
from pathlib import Path
import logging
import configparser
from logging.handlers import RotatingFileHandler


def read_config():
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(Path(__file__).parent.parent, "config/config.ini"))

        config_dict = dict()
        for section in config.sections():
            config_dict[section] = dict()
            for option in config.options(section):
                config_dict[section][option] = config.get(section, option)

        return config_dict
    except Exception as e:
        print("Exception while reading config file: %s" % str(e))


def applogger(config_dict):

    logs_dir = config_dict['Log']['path']
    logs_filename = config_dict['Log']['filename']

    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, logs_filename)

    handler = RotatingFileHandler(
        log_path, maxBytes=5*1024*1024, backupCount=5
    )

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger("my_streamlit_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
