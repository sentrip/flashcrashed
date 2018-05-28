import os
import random
from collections import deque

import numpy as np
import pandas as pd


def market_maker():
    directory = '/'.join([i for i in os.getcwd().replace('\\', '/').split('/')
                          if i not in {'flashcrashed', 'market', 'tests'}] +
                         ['flashcrashed', 'flashcrashed', 'market']) + '/'
    # Generated crashes from real market data
    with open(directory + 'prices.csv') as f:
        data = pd.read_csv(f, index_col=0)
    markets = []
    symbols = data['symbol'].unique()
    for symbol in symbols:
        _data = data[data['symbol'] == symbol]
        markets.append(_data['last_price'])

    # Real crashes that happened
    crashes = []
    for f in os.listdir(directory + 'real_crashes/'):
        with open(directory + 'real_crashes/' + f) as rf:
            data = pd.read_csv(rf, index_col=0)
            crashes.append(list(data['price']))

    cs = iter(crashes)

    def factory(real=False):
        nonlocal cs
        if real:
            try:
                return next(cs)
            except StopIteration:
                cs = iter(crashes)
                return next(cs)
        else:
            return iter(random.choice(markets))

    return factory


class FlashedMarket:
    def __init__(self, market, real=False):
        self.real = real
        self._market = market
        self.market = self._market
        self.last_price = 0
        self.position = 0
        self.crashes = []
        self.crashed = False

        self.drops = []
        self.rises = []
        self.crash_start = 0
        self.flash_ratio = 0
        self.drop_duration = 0
        self.rise_duration = 0
        self.min_price = 1e9

        self.return_count = 0
        self.returned_after = 25

        self.reset()

    def reset(self):
        self.crashed = False
        self.min_price = 1e9
        self.last_price = 0
        if not self.real:
            end = min(max(5000 - self.position, 0), 1300)
            if 5000 - self.position > 1100:
                self.crash_start = self.position + random.randint(500, end)
                self.flash_ratio = random.randint(5, 10)
                if random.random() < 0.5:
                    self.flash_ratio = random.randint(10, 100)
                self.drop_duration = random.randint(3, 5)
                if random.random() < 0.5:
                    self.drop_duration = random.randint(5, 15)
                self.rise_duration = random.randint(2, 5)
                if random.random() < 0.5:
                    self.rise_duration = random.randint(5, 50)

                self.drops = iter(self.random_offset(self.drop_duration, 0.8, order='exp'))
                self.rises = iter(self.random_offset(self.rise_duration, 0.6, reverse=True))
            self.market = self._market

        else:
            self.min_price = min(self._market)
            crashed = False
            prices = deque(maxlen=500)
            for i, price in enumerate(self._market):
                prices.append(price)
                if sum(prices) / len(prices) / price >= 1.1 and not crashed:
                    crashed = True
                    self.crash_start = i
                    self.drop_duration = self._market.index(self.min_price) - self.crash_start + 1
                elif price / (sum(prices) / len(prices)) >= 0.85 and crashed:
                    self.rise_duration = i - self.crash_start + self.drop_duration - 1
                    break
            self.flash_ratio = sum(self._market[:10]) / 10 / self.min_price
            self.market = iter(self._market)

    @staticmethod
    def random_offset(duration, volatility=0.5, reverse=False, order='linear'):
        sp = np.linspace if order == 'linear' else np.geomspace
        base_space = sp(0 + int(reverse) + 0.0001, 1 - int(reverse) + 0.0001, duration)
        space = base_space + base_space * (np.full([duration], 0.5) - np.random.rand(duration)) * volatility
        space[int(reverse) - 1] = min(space[int(reverse) - 1], 1)
        space[-int(reverse)] = max(space[-int(reverse)], 0)
        return space

    @property
    def crash_mid(self):
        return self.crash_start + self.drop_duration

    @property
    def crash_end(self):
        return self.crash_start + self.drop_duration + self.rise_duration

    @property
    def crashing(self):
        return self.crash_start < self.position <= self.crash_mid

    @property
    def rising(self):
        return self.crash_mid < self.position <= self.crash_end

    @property
    def returned(self):
        return self.crashed and (not self.crashing and not self.rising)

    def __iter__(self):
        return self

    def __next__(self):
        self.position += 1
        price = next(self.market)
        self.last_price = price
        if not self.real:
            if self.crashing:
                self.crashed = True
                price /= max(next(self.drops) * self.flash_ratio, 1)

            elif self.rising:
                price /= max(next(self.rises) * self.flash_ratio, 1)

            elif self.returned:
                self.return_count += 1
                if self.return_count >= self.returned_after:
                    crash = {'start': self.crash_start,  'drop_duration': self.drop_duration,
                             'rise_duration': self.rise_duration, 'ratio': self.flash_ratio, 'min_price': self.min_price}
                    if not self.crashes or crash['start'] != self.crashes[-1]['start']:
                        self.crashes.append(crash)
                    self.reset()
            if price < self.min_price:
                self.min_price = price
        else:
            if self.crashing:
                self.crashed = True
            elif self.returned:
                crash = {'start': self.crash_start,  'drop_duration': self.drop_duration,
                         'rise_duration': self.rise_duration, 'ratio': self.flash_ratio, 'min_price': self.min_price}
                if not self.crashes or crash['start'] != self.crashes[-1]['start']:
                    self.crashes.append(crash)
                self.crash_start = 0
                self.crashed = False
        return price
