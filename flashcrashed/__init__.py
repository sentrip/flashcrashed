# -*- coding: utf-8 -*-

"""Top-level package for flashcrashed."""
from contextlib import suppress
from gym.envs.registration import register
import gym.error

with suppress(gym.error.Error):  # env can only be registered once
    register(id='FlashGymGenerated-v1',
             entry_point='flashcrashed.market.env:FlashGym')
    register(id='FlashGymReal-v1',
             entry_point='flashcrashed.market.env:FlashGym',
             kwargs={'real': True})

__author__ = """Djordje Pepic"""
__email__ = 'djordje.m.pepic@gmail.com'
__version__ = '0.1.0'
