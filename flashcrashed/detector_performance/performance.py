import logging
import sys

import gym
from gym.envs.registration import register

from flashcrashed.detectors import *

if __name__ == "__main__":
    # LEVEL = 'ERROR'
    # log = logging.getLogger('flashcrashed')
    # log.setLevel(LEVEL)
    # stream = logging.StreamHandler(sys.stdout)
    # stream.setLevel(LEVEL)
    # stream.setFormatter(logging.Formatter(fmt='%(levelname)-8s: %(name)-15s: %(msg)s'))
    # log.addHandler(stream)

    detector = SimpleDetector()

    register(id='FlashGym-v1', entry_point='detector_performance.flashgym:FlashGym',)
    env = gym.make('FlashGym-v1')
    state = env.reset()
    done = False
    avg = 0
    crashed = False
    bought_in_crash = False
    sold_after_crash = True
    total_crashes = 0
    caught_crashes, caught_rises = 0, 0

    while not done:
        prediction = detector.predict(state[-1])
        state, reward, done, _ = env.step(prediction)
        if env.market.crashing and not crashed:
            crashed = True
            total_crashes += 1
        if env.market.crashing and not bought_in_crash and prediction == 0:
            caught_crashes += 1
            bought_in_crash = True
        if env.market.rising and not sold_after_crash and prediction == 2:
            caught_rises += 1
            sold_after_crash = True

        if not env.market.crashing and not env.market.rising:
            crashed, bought_in_crash, sold_after_crash = False, False, False

    print('Average reward: {:.2f}'.format(env.average_episode_reward))
    print('Total crashes: %d' % total_crashes)
    print('     - Caught buys : %d' % caught_crashes)
    print('     - Caught sells: %d' % caught_rises)
    print('     - Missed buys : %d' % (total_crashes - caught_crashes))
    print('     - Missed sells: %d' % (total_crashes - caught_rises))
