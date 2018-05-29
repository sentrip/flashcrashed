# -*- coding: utf-8 -*-

"""Console script for flashcrashed."""
import importlib
import logging
import logging.handlers
import os
import signal

from btfx_trader import get_symbols, PublicData
from pybeehive import Hive
import click
import gym

from .flashcrashed import TradeDataStreamer, TradeListener

TESTING = False


@click.command('Run flash-crash price watcher')
@click.argument('key')
@click.argument('secret')
@click.option('--type', default='tickers',
              help='Type of data to watch')
@click.option('--symbols', default='__get_all__',
              help='Cryptocurrency symbols to monitor for flash crashes '
                   '(by default it monitors all symbols)')
@click.option('--detector',
              default='flashcrashed.detector.BasicDetector',
              help='Class to use for detecting flash crashes')
@click.option('--notifier',
              default='flashcrashed.flashcrashed.NotificationListener',
              help='Class to use to notify that a flash crash has occurred')
@click.option('--log-level', default='INFO',
              help='Logging level of application')
@click.option('--log-file', default='log.txt',
              help='File to output main logs of application')
@click.option('--crash-log-file', default='crash_log.txt',
              help='File to output logs of any crashes that occur')
def main(key, secret, type, symbols, detector, notifier,
         log_level, log_file, crash_log_file):
    """Console script for flashcrashed."""

    hive = Hive()
    if symbols == '__get_all__':
        symbols = get_symbols()
    else:
        symbols = symbols.split(',')

    click.echo(
        "Running flashcrashed price-watcher for %d symbols" % len(symbols)
    )

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

    if not TESTING:
        _setup_logging(log_level, log_file, crash_log_file)

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

    click.echo(
        "Running flashcrashed performance "
        "evaluation on detector at '%s'" % detector
    )
    click.echo('Number of generated episodes: %d' % episodes[0])
    click.echo('Number of real episodes: %d' % episodes[1])

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


def _setup_logging(log_level, log_file, crash_log_file):
    log = logging.getLogger('flashcrashed')
    trade_log = logging.getLogger('btfx_trader')
    crash_log = logging.getLogger('flashcrashed.crash')
    crash_log.propagate = False

    for l in [log, trade_log, crash_log]:
        l.setLevel(log_level)

    formatter = logging.Formatter(
        fmt='%(asctime)-15s: %(levelname)-8s: %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S'
    )

    handler = logging.handlers.RotatingFileHandler(
        log_file, mode='a', maxBytes=1024 * 1024)
    crash_handler = logging.handlers.RotatingFileHandler(
        crash_log_file, mode='a', maxBytes=1024 * 1024)

    for h in [handler, crash_handler]:
        h.setLevel(log_level)
        h.setFormatter(formatter)

    log.addHandler(handler)
    trade_log.addHandler(crash_handler)
    crash_log.addHandler(crash_handler)
