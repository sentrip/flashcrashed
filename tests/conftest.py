import os, sys
sys.path.append(os.path.abspath('../flashcrashed'))
import pytest
import time
import random
import gym
from functools import partial
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
    def __init__(self, *args, long=False, **kwargs):
        self.val = 50
        self.count = 0
        self.connected = True
        self.start = 450 if not long else 4500
        self.end = 500 if not long else 4550

    def connect(self):
        pass

    def close(self):
        pass

    def get(self, _type, _symbol):
        self.count += 1
        if self.start < self.count < self.end:
            return {'bid': self.val / 10}
        return {'bid': self.val}


class FakeTrader:
    calls = []

    def __init__(self, *args, **kwargs):
        self.calls.clear()

    def connect(self):
        pass

    def order(self, symbol, price, ratio=0, **kwargs):
        self.calls.append(('SELL' if ratio < 0 else 'BUY', abs(ratio)))

    def wait_execution(self, _id):
        return {'executed': 10, 'execution_price': 10}

    def close(self):
        pass


class FakeMessages:
    calls = []

    def create(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class FakeTwilioClient:
    def __init__(self, *args, **kwargs):
        self.messages = FakeMessages()


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


@pytest.fixture
def patched_bitfinex(monkeypatch):

    def _get_symbols():
        return ['BTCUSD']
    os.environ['TWILIO_SID'], os.environ['TWILIO_SECRET'] = '', ''
    os.environ['NUMBER'], os.environ['TWILIO_NUMBER'] = '', ''

    monkeypatch.setattr('flashcrashed.flashcrashed.Trader', FakeTrader)
    monkeypatch.setattr('flashcrashed.flashcrashed.Client', FakeTwilioClient)
    monkeypatch.setattr('flashcrashed.cli.get_symbols', _get_symbols)
    monkeypatch.setattr('flashcrashed.cli.PublicData', partial(FakeApi, long=True))
    yield FakeTrader, FakeMessages

