import json
import logging
import sys


def load_config():
    with open('flashcrashed/documents/config.json') as f:
        return json.load(f)


def setup_log(cls):
    """Basic log setup - streams to stdout"""
    cls.log = logging.getLogger(cls.__class__.__name__)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(cls.log_level)
    logging.basicConfig(level=cls.log_level, handlers=[sh])


if __name__ == '__main__':
    import time
    from multiprocessing.connection import Client

    from prices.prices import Prices
    q = Prices()

    q.start()

    c = Client(('localhost', 1337), authkey=b'prices')

    start = time.time()
    while time.time() - start < 60:
        print(c.recv())

    c.close()

    q.close()
