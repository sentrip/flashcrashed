from pybeehive import Streamer, Listener, Event
from btfx_trader import Trader
from twilio.rest import Client
import os

from .detector import BasicDetector


_type_key_map = {
    'tickers': 'bid',
    'trades': 'price'
}


class TradeDataStreamer(Streamer):
    def __init__(self, _type, symbol, data, topic=None):
        super(TradeDataStreamer, self).__init__(topic=topic)
        self.type = _type
        self.symbol = symbol
        self.data = data
        self.key = _type_key_map.get(_type, 'close')

    def stream(self):
        while self.alive:
            data = self.data.get(self.type, self.symbol)
            yield Event((self.symbol, data[self.key]))


class TradeListener(Listener):
    def __init__(self, key, secret, detector_class=BasicDetector, filters=None):
        super(TradeListener, self).__init__(filters=filters)
        self.trader = Trader(key, secret)
        self.detector_class = detector_class
        self.detectors = {}
        self.trading = {}

    def on_price(self, symbol, price):
        if symbol not in self.detectors.keys():
            self.detectors[symbol] = self.detector_class()
            self.detectors[symbol].symbol = symbol
            self.trading[symbol] = False

        prediction = self.detectors[symbol].predict(price)
        if prediction == 0 and not any(k for k in self.trading.values()):
            self.trading[symbol] = True
            _id = self.trader.order(symbol, price, ratio=1, pad_price=0.03)
            order = self.trader.wait_execution(_id)
            return Event((symbol, 'BOUGHT', order))

        elif prediction == 2 and self.trading[symbol]:
            self.trading[symbol] = False
            _id = self.trader.order(symbol, price, ratio=-1, pad_price=0.01)
            order = self.trader.wait_execution(_id)
            return Event((symbol, 'SOLD', order))

    def setup(self):
        self.trader.connect()

    def teardown(self):
        self.trader.close()

    def on_event(self, event):
        return self.on_price(*event.data)


class NotificationListener(Listener):
    @staticmethod
    def notify_traded(symbol, action, order):
        key, secret = os.environ['TWILIO_SID'], os.environ["TWILIO_SECRET"]
        Client(key, secret).messages.create(
            to=os.environ['NUMBER'],
            from_=os.environ['TWILIO_NUMBER'],
            body='%s was %s at $%.2f for $%.2f!' % (
                symbol, action, order['execution_price'],
                abs(order['executed'] * order['execution_price'])
            )
        )

    def on_event(self, event):
        if event.data:
            self.notify_traded(*event.data)
