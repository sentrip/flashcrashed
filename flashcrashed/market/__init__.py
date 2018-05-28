import gym.error
from gym.envs.registration import register
# try:
register(id='FlashGymGenerated-v1', entry_point='flashcrashed.market.env:FlashGym')
register(id='FlashGymReal-v1', entry_point='flashcrashed.market.env:FlashGym', kwargs={'real': True})
# except (gym.error.Error, ImportError):
#     try:
#         register(id='FlashGymGenerated-v1', entry_point='market.env:FlashGym')
#         register(id='FlashGymReal-v1', entry_point='flashcrashed.market.env:FlashGym', kwargs={'real': True})
#     except (gym.error.Error, ImportError):
#         print('Could not import FlashGym!')

