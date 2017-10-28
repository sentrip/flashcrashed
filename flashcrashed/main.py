from collections import defaultdict
from multiprocessing.connection import Client
from queue import Queue

from prices import Prices
from trade import FlashCoinTrader, Thread


class FlashSocketDistributor(Thread):
    def __init__(self):
        super(FlashSocketDistributor, self).__init__()
        self.conn = Client(('localhost', 1337), authkey=b'prices')
        self.queues = defaultdict(Queue)

    def run(self):
        while True:
            ticker, data = self.conn.recv()
            self.queues[ticker].put(data[-2])


if __name__ == '__main__':
    import time
    prices = Prices()
    prices.start()
    q = FlashSocketDistributor()
    q.start()
    time.sleep(10)
    for t in q.queues:
        FlashCoinTrader(q.queues[t]).start()
