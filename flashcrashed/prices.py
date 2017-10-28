from multiprocessing.connection import Listener
from threading import Thread, Lock

from crypto import CoinStream
from flashcrashed import setup_log, load_config


class Prices:

    def __init__(self):
        # Add all the different sources of price data here
        self.streams = [
            CoinStream()
        ]

        self.server = Listener(('localhost', 1337), authkey=b'prices')
        self.log_level = load_config()['log_level']
        self.conns = []
        self.workers = []
        self.running = True
        self._mutex = Lock()
        self.log = None
        setup_log(self)

    def _connect(self):
        while self.running:
            try:
                self.log.debug('Connecting to client...')
                self.conns.append(self.server.accept())
                self.log.debug('Successfully connected to client')
            except ConnectionError:
                self.log.debug('Stopping client listener')

    def connect(self):
        Thread(target=self._connect).start()

    def send_from_queue(self, ticker):
        while self.running:
            for stream in self.streams:
                data = stream.get(ticker)
                for conn in self.conns:
                    with self._mutex:
                        self.log.debug('Sending data for %s', ticker)
                        try:
                            for datum in reversed(data):
                                conn.send((ticker, datum))
                            self.log.debug('Successfully sent data')
                        except ConnectionError:
                            self.conns.remove(conn)
                            self.log.debug('Client connection dropped')

    def start(self):
        self.connect()
        for stream in self.streams:
            stream.connect()
            for ticker in stream.tickers:
                w = Thread(target=self.send_from_queue, args=(ticker,))
                w.start()
                self.workers.append(w)

    def close(self):
        self.running = False
        for w in self.workers:
            w.join()
        for stream in self.streams:
            stream.shutdown()
        self.log.info('Successfully shut down')
