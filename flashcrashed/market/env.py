import gym.spaces
from gym.utils import seeding

from .gen import market_maker, FlashedMarket


class FlashGym(gym.Env):
    def __init__(self, real=False):
        self.real = real
        self.maker = market_maker()
        self.market = None

        self.wait = 0
        self.last_price = 0
        self.crashes_length = 0

        self.bought, self.sold = False, False
        self.buy_price, self.sell_price = 0, 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human'):
        pass

    def reset(self):
        self.wait = 0
        self.crashes_length = 0
        self.market = FlashedMarket(self.maker(real=self.real), self.real)
        self.bought, self.sold = False, False
        self.buy_price, self.sell_price = 0, 0
        self.last_price = next(self.market)
        return self.last_price

    def step(self, action):
        if action == 0:
            reward = self.buy_reward
        elif action == 2:
            reward = self.sell_reward
        else:
            reward = 0
        ln = len(self.market.crashes)
        if ln and ln != self.crashes_length:
            self.crashes_length = ln
            if self.buy_price != 0:
                roi = round(self.sell_price / self.buy_price * 100, 2)
            else:
                roi = 0
            self.market.crashes[-1].update(bought=self.bought, sold=self.sold, roi=roi)
            self.bought, self.sold = False, False
        try:
            self.last_price = next(self.market)
            done = False
        except StopIteration:
            done = True
        return self.last_price, reward, done, {}

    @property
    def buy_reward(self):
        if not self.market.crashing:
            return -1
        if self.bought:
            return -0.1
        self.bought = True
        self.buy_price = self.last_price
        return 1 - 2 * abs(self.market.position - self.market.crash_mid) / self.market.drop_duration

    @property
    def sell_reward(self):
        if not self.market.rising and not self.market.returned:
            return -1
        if self.sold or not self.bought:
            return -0.1
        self.sold = True
        self.sell_price = self.last_price
        if self.real:
            return int(self.buy_price <= self.sell_price * 3) * 2 - 1.
        return 1 - 2 * max(self.market.crash_end - self.market.position, 0) / self.market.rise_duration
