import time
from collections import deque

from btfxwss import BtfxWss

from flashcrashed import load_config, setup_log


class CoinStream:
    btfxwss_log_level = 'CRITICAL'

    def __init__(self):
        config = load_config()
        self.log_level = config['log_level']
        self.tickers = config['tickers']
        # No api keys required for reading public data
        self.api = BtfxWss("", "", log_level=self.btfxwss_log_level)
        self.queues = {}
        self.seen = deque(maxlen=3000)

        self.log = None
        setup_log(self)

    def connect(self):
        """Connects to btfxwss api and subscribes to OHLCV ticker queues for each coin specified in config.json"""
        self.api.start()
        self.log.debug('Waiting for connection...')
        while not self.api.conn.connected.is_set():
            time.sleep(0.1)
        self.log.debug('Subscribing to tickers...')
        for ticker in self.tickers:
            self.api.subscribe_to_candles(ticker)
        self.log.debug('Waiting on connections of tickers...')
        time.sleep(5)
        self.log.debug('Done waiting, setting up socket queues for tickers')
        for ticker in self.tickers:
            self.queues[ticker] = self.api.candles(ticker)
        self.log.debug('Done setting up queues, waiting on first data...')
        while any(q.empty() for q in self.queues.values()):
            time.sleep(0.01)
        self.log.info('Successfully initialized ')

    def shutdown(self):
        """Un-subscribes from all queues and shuts down btfxwss api"""
        self.log.debug('Un-subscribing from all tickers...')
        for ticker in self.tickers:
            self.api.unsubscribe_from_candles(ticker)
        self.log.debug('Shutting down api socket...')
        self.api.stop()
        self.log.info('Successfully shut down')

    def get(self, ticker):
        """Gets next ticker datum from queue for provided coin name"""
        self.log.debug('Getting from %s queue', ticker)
        data, _ = self.queues[ticker].get()
        while data in self.seen:
            self.log.debug('Filtering already seen tick from %s queue', ticker)
            data, _ = self.queues[ticker].get()
        data = [data[0][1:]] if isinstance(data[0][0], int) else [i[1:] for i in data[0]]
        self.seen.append(data)
        self.log.debug('Received data from %s queue', ticker)
        return data
