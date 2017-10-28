import json
import logging
import sys


def load_config():
    with open('documents/config.json') as f:
        return json.load(f)


def setup_log(cls):
    """Basic log setup - streams to stdout"""
    cls.log = logging.getLogger(cls.__class__.__name__)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(cls.log_level)
    logging.basicConfig(level=cls.log_level, handlers=[sh])
