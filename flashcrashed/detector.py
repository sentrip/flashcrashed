# todo add logging for detector

class SMADetector:
    def __init__(self):
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

    def simple_moving_average(self, n):
        return sum(self.prices[-n:]) / n

    @property
    def means(self):
        return [self.simple_moving_average(r) for r in self.lengths]

    def detect_crash(self, price):
        if list(reversed(sorted(self.means))) == self.means:
            if sum(self.prices) / len(self.prices) / price > self.drop_threshold:
                self.crashed = True
                return True
        return False

    def detect_rise(self, price):
        if self.crashed and price > sum(self.prices[self.crash_start - 100:self.crash_start]) / 100 * 0.8:
            return True
        return False

    def predict(self, price):
        self.prices.append(price)
        if len(self.prices) > 5000:
            self.prices = self.prices[-5000:]

        if self.crashed:
            self.crash_start -= 1

        if self.waiting_to_buy:
            self.wait += 1
            if price >= self.last_price * 0.95 and self.wait > 2:
                self.waiting_to_buy = False
                self.wait = 0
                return -1

        if self.detect_crash(price):
            self.waiting_to_buy = True

        elif self.detect_rise(price):
            self.rise_count += 1
            if self.crashed and self.rise_count > 5:
                self.crash_start = -min(self.lengths)
                self.crashed = False
                return 1
        else:
            self.rise_count = 0
        self.last_price = price
        return 0
