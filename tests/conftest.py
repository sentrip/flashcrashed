import os, sys
sys.path.append(os.path.abspath('../flashcrashed'))
import pytest
import time
import random
import gym
import flashcrashed.market
from flashcrashed.market.gen import market_maker as maker
from flashcrashed.detector import *
from flashcrashed.flashcrashed import TradeListener

DETECTORS = [BasicDetector]


def pytest_generate_tests(metafunc):
    if 'env' in metafunc.fixturenames:
        metafunc.parametrize('env', [
            gym.make('FlashGymGenerated-v1'),
            gym.make('FlashGymReal-v1')
        ])
    elif 'detector' in metafunc.fixturenames:
        metafunc.parametrize('detector', [d() for d in DETECTORS])


@pytest.fixture
def market_maker():
    return maker()


class FakeApi:
    def __init__(self):
        self.val = 50
        self.count = 0
        self.connected = True

    def get(self, _type, _symbol):
        time.sleep(random.random() / 1000)
        self.count += 1
        if 450 < self.count < 500:
            return {'price': self.val / 10}
        return {'price': self.val}


class FakeTrader:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def connect(self):
        pass

    def buy(self, percentage):
        self.calls.append(('BUY', percentage))

    def sell(self, percentage):
        self.calls.append(('SELL', percentage))

    def order(self, symbol, price, ratio=0, **kwargs):
        self.calls.append(('SELL' if ratio < 0 else 'BUY', abs(ratio)))

    def wait_execution(self, _id):
        pass

    def close(self):
        pass


@pytest.fixture
def trader():
    t = TradeListener('key', 'secret')
    t.trader = FakeTrader()
    return t


@pytest.fixture
def api():
    return FakeApi()


@pytest.fixture
def apis():
    return [FakeApi() for _ in range(20)]
