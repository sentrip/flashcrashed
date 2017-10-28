# todo add logging for trade
from threading import Thread

from detector import SMADetector as Detector


class CoinTrade:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def buy(self, percentage):
        self.key = self.key
        print('Buying {}'.format(percentage))

    def sell(self, percentage):
        self.key = self.key
        print('Selling {}'.format(percentage))


class FlashCoinTrader(Thread):
    def __init__(self, queue, *args, **kwargs):
        super(FlashCoinTrader, self).__init__(*args, **kwargs)
        self.queue = queue
        self.detector = Detector()
        self.client = CoinTrade("", "")

    def run(self):
        while True:
            price = self.queue.get()
            prediction = self.detector.predict(price)
            if prediction == -1:
                self.client.buy(1.0)
            elif prediction == 1:
                self.client.sell(1.0)
            else:
                print('Doing nothing...')
