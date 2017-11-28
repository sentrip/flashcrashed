from flashcrashed.api import setup_log


class SimpleDetector:
    log = None

    def __init__(self, log_level='DEBUG'):
        self.prices = []
        self.lengths = [50, 20, 10, 5]
        self.drop_threshold = 4.9

        self.crashed = False
        self.risen = False
        self.crash_start = -min(self.lengths)
        self.rise_count = 0

        self.waiting_to_buy = False
        self.last_price = 0
        self.wait = 0
        self.buy_cool_down = 100
        self.last_buy = 0
        self.position = 0

        setup_log(self, log_level)

    def simple_moving_average(self, n):
        return sum(self.prices[-n:]) / n

    @property
    def means(self):
        return [self.simple_moving_average(r) for r in self.lengths]

    def detect_crash(self, price):
        self.log.debug('Checking for flash crash on price %s', str(price))
        if list(reversed(sorted(self.means))) == self.means:
            if sum(self.prices) / len(self.prices) / price > self.drop_threshold:
                self.crashed = True
                return True
        self.log.debug('No crash was detected')
        return False

    def detect_rise(self, price):
        self.log.debug('Checking for rise on price %s', str(price))
        if self.crashed and price > sum(self.prices[self.crash_start - 100:self.crash_start]) / 100 * 0.8:
            return True
        self.log.debug('No rise was detected')
        return False

    def predict(self, price):
        self.position += 1
        self.prices.append(price)
        if len(self.prices) > 5000:
            self.prices = self.prices[-5000:]

        if self.crashed:
            self.crash_start -= 1

        if self.waiting_to_buy and self.crashed:
            self.log.info('Crash detected, waiting %s more ticks to buy', str(3 - self.wait))
            self.wait += 1
            if price >= self.last_price * 0.95 and self.wait > 4 and self.position > self.buy_cool_down:
                self.log.critical('FLASHCRASH OCCURRED!!! SUBMITTING BUY  ORDER AT PRICE OF %.2f', price)
                self.waiting_to_buy = False
                self.wait = 0
                self.position = 0
                return 0

        if self.detect_crash(price):
            if not self.waiting_to_buy:
                self.log.info('Crash detected, moving to second stage detection')
            self.waiting_to_buy = True

        elif self.detect_rise(price):
            if not self.rise_count:
                self.log.info('Rise detected, moving to second stage detection')
            self.rise_count += 1
            self.log.info('Rise detected, waiting %s more ticks to buy', str(5 - self.rise_count))
            if self.crashed and self.rise_count > 5:
                self.log.critical('FLASHCRASH REBOUND!!!! SUBMITTING SELL ORDER AT PRICE OF %.2f', price)
                self.crash_start = -min(self.lengths)
                self.crashed = False
                return 2
        else:
            self.rise_count = 0
        self.last_price = price
        return 1
