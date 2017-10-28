from datetime import datetime
from multiprocessing.connection import Client

from sqlalchemy import create_engine, Table, MetaData, Column, Float, DateTime

from flashcrashed import load_config


# todo add logging for coin database


class CoinBase:
    def __init__(self):
        self.incoming = Client(('localhost', 1337), authkey=b'coin')
        self.tables = {}
        self.table_names = ['open', 'low', 'high', 'close', 'volume']

        config = load_config()
        self.tickers = config['tickers']

        self.db = create_engine(config['Database_path'])
        self.db.echo = False

        for ticker in self.tickers:
            self.tables[ticker] = Table(ticker, MetaData(self.db), Column('time', DateTime, primary_key=True),
                                        *[Column(i, Float) for i in self.table_names])
            if ticker not in self.db.table_names():
                self.tables[ticker].create()

    def update(self, ticker, data):
        current_time = datetime.now()
        data = dict(zip(self.table_names, data))
        data.update(time=current_time)
        i = self.tables[ticker].insert()
        i.execute(data)

    def run(self):
        while True:
            try:
                ticker, data = self.incoming.recv()
                self.update(ticker, data)
            except ConnectionError:
                break
