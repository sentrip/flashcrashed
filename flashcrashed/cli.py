# -*- coding: utf-8 -*-

"""Console script for flashcrashed."""
import importlib
import logging
import sys
import signal

from btfx_trader import get_symbols, PublicData
from pybeehive import Hive
import click

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


def _import_class(path):
    *path, class_name = path.split('.')
    module = importlib.import_module('.'.join(path))
    return getattr(module, class_name)
