# -*- coding: utf-8 -*-

"""Console script for flashcrashed."""
import importlib
import logging
import os
import sys
import signal

from btfx_trader import get_symbols, PublicData
from pybeehive import Hive
import click
import gym

from .flashcrashed import TradeDataStreamer, TradeListener


@click.command('Run flash-crash price watcher')
@click.argument('key')
@click.argument('secret')
@click.option('--type', default='tickers',
              help='Type of data to watch')
@click.option('--symbols', default='__get_all__',
              help='Cryptocurrency symbols to monitor for flash crashes '
                   '(by default it monitors all symbols)')
@click.option('--detector', default='flashcrashed.detector.BasicDetector',
              help='Class to use for detecting flash crashes')
@click.option('--notifier',
              default='flashcrashed.flashcrashed.NotificationListener',
              help='Class to use to notify that a flash crash has occurred')
def main(key, secret, type, symbols, detector, notifier):
    """Console script for flashcrashed."""
    click.echo("")

    hive = Hive()
    if symbols == '__get_all__':
        symbols = get_symbols()
    else:
        symbols = symbols.split(',')

    trade_data = PublicData(types=[type], symbols=symbols)
    for symbol in symbols:
        hive.add(TradeDataStreamer(type, symbol, trade_data))

    detector_class = _import_class(detector)
    notifier_class = _import_class(notifier)

    trade = TradeListener(key, secret, detector_class=detector_class)
    notify = notifier_class()
    trade.chain(notify)
    hive.add(trade)
    signal.signal(signal.SIGINT, lambda *a, **kwa: hive.close())

    # todo: setup logging

    trade_data.connect()
    hive.run()
    trade_data.close()

    return 0


@click.command('Evaluate performance of flash-crash detector '
               'on generated and real flash crash data')
@click.option('--detector', default='flashcrashed.detector.BasicDetector',
              help='Class to use for detecting flash crashes')
@click.option('--episodes', default=5,
              help='Number of generated flash crash episodes to run')
def performance(detector, episodes):
    names = ['FlashGymGenerated-v1', 'FlashGymReal-v1']
    kwargs = [{}, {'real': True}]
    episodes = [episodes, len(os.listdir(
        os.path.join(os.path.abspath(__name__.split('.')[0]),
                     'market/real_crashes')
    ))]
    detector = _import_class(detector)()

    for gym_name, kw, n_episodes in zip(names, kwargs, episodes):
        env = gym.make(gym_name)
        missed_crashes = []
        rewards, rois, catches = [], [], []
        crashes, caught_buys, caught_sells = 0, 0, 0
        for _ in range(n_episodes):
            price = env.reset()
            detector.reset()
            avg, steps = 0, 0
            done = False

            while not done:
                prediction = detector.predict(price)
                price, reward, done, _ = env.step(prediction)
                avg += reward
                if reward != 0:
                    steps += 1

            avg_roi = sum([i.get('roi', 0)
                           for i in env.market.crashes]
                          ) / len(env.market.crashes)
            flash_capital = sum([i.get('roi', 0) / i.get('ratio', 1)
                                 for i in env.market.crashes]
                                ) / len(env.market.crashes)
            caught_buy = len([i for i in env.market.crashes
                              if 'bought' in i and i['bought']])
            caught_sell = len([i for i in env.market.crashes
                               if 'sold' in i and i['sold']])
            missed_crashes.extend(i for i in env.market.crashes
                                  if not ('sold' in i
                                          and i['sold']
                                          and 'bought' in i
                                          and i['bought'])
                                  )
            crashes += len(env.market.crashes)
            caught_buys += caught_buy
            caught_sells += caught_sell
            rewards.append(avg / max(steps, 1))
            rois.append(avg_roi)
            catches.append(flash_capital)

        click.echo('\n' + gym_name)
        click.echo('Total crashes   : %d' % crashes)
        click.echo('Average reward  : {:.2f}'.format(
            sum(rewards) / len(rewards)))
        click.echo('Average roi (%) : {:.2f}'.format(
            max(sum(rois) / len(rois) - 100, 0)))
        click.echo('Average catch (%): {:.2f}'.format(
            sum(catches) / len(catches)))
        click.echo('     - Caught buys : %d' % caught_buys)
        click.echo('     - Caught sells: %d' % caught_sells)
        click.echo('     - Missed buys : %d' % (crashes - caught_buys))
        click.echo('     - Missed sells: %d' % (crashes - caught_sells))

        if len(missed_crashes) > 0:
            click.echo('\n' + '#' * 40 + ' MISSED CRASHES ' + '#' * 40)
            for crash in sorted(missed_crashes, key=lambda i: 1. / i['ratio']):
                click.echo(
                    'Ratio: %3d, Drop duration: %2d, Rise duration: %3d, '
                    'Bought %d, Sold %d, Minimum price: %.2f' % (
                            crash['ratio'],
                            crash['drop_duration'],
                            crash['rise_duration'],
                            int(crash.get('bought', False)),
                            int(crash.get('sold', False)),
                            crash['min_price']
                    ))
            click.echo('\n')


def _import_class(path):
    *path, class_name = path.split('.')
    module = importlib.import_module('.'.join(path))
    return getattr(module, class_name)
