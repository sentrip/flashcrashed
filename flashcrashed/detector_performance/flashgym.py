import math

import gym
import gym.spaces
import numpy as np
from gym.utils import seeding

from detector_performance.market_gen import FlashedMarket


class FlashGym(gym.Env):
    def __init__(self):
        self.history_length = 1000
        self.history = np.zeros([self.history_length])
        self.changes = [500, 200, 50, 20, 10, 5, 2]
        self.episode_length = 0
        self.episode_reward = 0
        self.market = None

        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(
            np.array([-np.finfo(np.float32).max] * (len(self.changes) + 1), dtype=np.float32),
            np.array([np.finfo(np.float32).max] * (len(self.changes) + 1), dtype=np.float32)
        )

    def change(self, price, distance):
        i = min(int(math.ceil(distance)*0.6), 10)
        mu = sum(self.history[-distance-i:-distance+i]) / 2 / i
        return (price - mu) / max(mu, 1)

    @property
    def state(self):
        state = [self.change(self.history[-1], d) for d in self.changes] + [self.history[-1]]
        return np.array(state)

    def _reset(self):
        self.episode_length = 100000
        self.episode_reward = 0
        self.market = FlashedMarket()
        self.market.crash_start += self.history_length
        for _ in range(self.history_length):
            np.roll(self.history, -1)
            self.history[-1] = next(self.market)
        return self.state

    def _step(self, action):
        if action == 0:
            reward = self.market.buy_reward
        elif action == 2:
            reward = self.market.sell_reward
        else:
            reward = 0
        self.episode_reward += reward
        np.roll(self.history, -1)
        self.history[-1] = next(self.market)
        done = self.market.total_pos > self.episode_length
        return self.state, reward, done, {}

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    @property
    def average_episode_reward(self):
        return self.episode_reward / self.market.n_crashes / 2
