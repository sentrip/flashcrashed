from gym.envs.registration import register
register(id='FlashGymGenerated-v1', entry_point='flashcrashed.market.env:FlashGym')
register(id='FlashGymReal-v1', entry_point='flashcrashed.market.env:FlashGym', kwargs={'real': True})
