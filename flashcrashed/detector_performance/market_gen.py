import math
import random


def random_market():
    price = random.random() * 5000 + 50
    ratio = price / 500 + 0.9
    cycles = [
        {'length': 7, 'variance': 50 * ratio * 0.1, 'noise': 1, 'trend': 0, 'phase': random.random() * math.pi},
        {'length': 365, 'variance': 30 * ratio * 0.2, 'noise': 1, 'trend': 0, 'phase': random.random() * math.pi},
        {'length': 700, 'variance': 2 * ratio * 0.5, 'noise': 0, 'trend': 100, 'phase': random.random() * math.pi}
    ]
    for cycle in cycles:
        cycle['increment'] = math.pi / cycle['length']
    while True:
        for cycle in cycles:
            cycle['phase'] += cycle['increment'] * (random.random() * 2 - 1)
            ratio = (random.random() * 2 - 1) * cycle['noise'] + cycle['trend'] / cycle['length']
            price += math.sin(cycle['phase']) * cycle['variance'] / cycle['length'] * ratio
        yield price


class FlashCrash:
    def __init__(self):
        self.position = 0
        self.duration = random.randint(20, 100)
        self.delta = math.pi / self.duration

        self.flash_ratio = random.randint(5, 10)
        if random.random() < 0.5:
            self.flash_ratio = random.randint(10, 20)
        elif random.random() < 0.05:
            self.flash_ratio = random.randint(20, 100)
        elif random.random() < 0.01:
            self.flash_ratio = random.randint(100, 1000)

    def convert(self, price):
        self.position += 1
        if self.position > self.duration:
            return price
        return price / max(1, self.flash_ratio * math.sin(self.position * self.delta * 0.9))


class FlashedMarket:
    def __init__(self):
        self.market = random_market()
        self.crash_start = random.randint(200, 1000)
        self.position = 0
        self.total_pos = 0

        self.crash = FlashCrash()
        self.bought, self.sold = False, False
        self.n_crashes = 0

    @property
    def crash_mid(self):
        return self.crash_start + self.crash.duration / 2
    
    @property
    def crash_end(self):
        return self.crash_start + self.crash.duration
    
    @property
    def crashing(self):
        return self.crash_start < self.position < self.crash_end

    @property
    def after_crash(self):
        return self.position >= self.crash_end + 20
    
    @property
    def rising(self):
        return self.crash_mid < self.position < self.crash_end + 20
    
    @property
    def buy_reward(self):
        if not self.crashing:
            return -10
        if self.bought:
            return -0.1
        self.bought = True
        return 1 - 2 * abs(self.position - self.crash_mid) / self.crash.duration

    @property
    def sell_reward(self):
        if not self.rising:
            return -10
        if self.sold:
            return -0.1
        self.sold = True
        return 1 - 2 * max(self.crash_end - self.position, 0) / self.crash.duration

    def __iter__(self):
        return self

    def __next__(self):
        self.total_pos += 1
        self.position += 1
        price = next(self.market)

        if self.after_crash:
            self.position = 0
            self.crash_start = random.randint(500, 3000)
            self.crash = FlashCrash()
            self.bought, self.sold = False, False
            self.n_crashes += 1
        elif self.crashing:
            price = self.crash.convert(price)

        return max(1, price)
