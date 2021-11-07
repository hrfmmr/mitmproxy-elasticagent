import json
import logging
import logging.config


def setup_logger():
    with open("conf/dev.logging.conf.json") as f:
        log_conf = json.load(f)
        logging.config.dictConfig(log_conf)
