import logging
import os
import queue
import time
from threading import Thread

from btfx_trader import Trader

from .detectors import SimpleDetector

log = logging.getLogger('flashcrashed')


class FlashCoinTrader(Thread):

    def __init__(self, api, symbol, kill_queue):
        super(FlashCoinTrader, self).__init__()
        self.api = api
        self.symbol = symbol
        self.kill_queue = kill_queue

        self.detector = SimpleDetector()
        #self.trader = Trader(symbol, (os.environ['BTFX_KEY'], os.environ['BTFX_SECRET']))
        self.trader = type('', (), {'buy': lambda *a: None, 'sell': lambda *a: None})

    def run(self):
        no_change = 0
        while not self.api.connected:
            time.sleep(0.1)
        while True:
            try:
                self.kill_queue.get_nowait()
                self.kill_queue.task_done()
                break
            except queue.Empty:
                price = self.api.get(self.symbol, 'tickers')['last_price']
                prediction = self.detector.predict(price)
                log.debug('Next market step, price %.2f, prediction %d', price, prediction)
                if prediction == 0:
                    self.trader.buy(1.0)
                elif prediction == 2:
                    self.trader.sell(1.0)
                else:
                    no_change += 1
                    if no_change > 11:
                        log.info('No changes detected, doing nothing...   %s - %.2f' % (self.symbol, price))
                        no_change = 0
