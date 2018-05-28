import logging
from abc import ABC, abstractmethod
from collections import deque

log = logging.getLogger('flashcrashed')
crash_log = logging.getLogger("flashcrashed.crash")


class Detector(ABC):
    def __init__(self):
        self.symbol = 'Default'  # for logging purposes
        self.last_action = None
        self._count = 0
        self._log_same_every = 10

    @abstractmethod
    def reset(self):
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def _predict(self, price):
        raise NotImplementedError  # pragma: nocover

    def predict(self, price):
        action = self._predict(price)
        if action == 0:
            crash_log.info('%6s - CRASH detected at %.2f' % (self.symbol, price))
        elif action == 2:
            crash_log.info('%6s - RISE detected at %.2f' % (self.symbol, price))
        else:
            log.info('%6s - Doing nothing at %.2f' % (self.symbol, price))

        self._count += 1
        if action == self.last_action == 1:
            if self._count % self._log_same_every != 0:
                return action
        self.last_action = action
        return action


class BasicDetector(Detector):
    drop_ratio = 3
    resell_ratio = 2.75
    history_length = 150

    def __init__(self):
        super(BasicDetector, self).__init__()
        self.prices = deque(maxlen=self.history_length)
        self.bought = False
        self.buy_price = 0.

    def reset(self):
        self.prices = deque(maxlen=self.history_length)
        self.bought = False
        self.buy_price = 0.

    def _predict(self, price):
        self.prices.append(price)
        avg_price = sum(list(sorted(self.prices))[-int(self.history_length/2):]) / int(self.history_length/2)
        if price <= avg_price / self.drop_ratio and len(self.prices) == self.prices.maxlen and not self.bought:
            self.bought = True
            self.buy_price = price
            return 0
        if price >= self.buy_price * self.resell_ratio and self.bought:
            self.bought = False
            self.buy_price = 0
            return 2
        return 1
