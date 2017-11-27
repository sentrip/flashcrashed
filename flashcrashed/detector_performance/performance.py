import gym
from gym.envs.registration import register

from flashcrashed.detectors import *

if __name__ == "__main__":
    detector = SimpleDetector()

    register(id='FlashGym-v1', entry_point='detector_performance.flashgym:FlashGym',)
    env = gym.make('FlashGym-v1')
    state = env.reset()
    done = False
    avg = 0
    while not done:
        prediction = detector.predict(state[-1])
        state, reward, done, _ = env.step(prediction)
    print('Average reward: {:.2f}'.format(env.average_episode_reward))
