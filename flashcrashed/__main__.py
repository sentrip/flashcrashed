import argparse
import logging
import time
from queue import Queue

from btfx_trader import CoinAPI

from .flashtrader import FlashCoinTrader

parser = argparse.ArgumentParser(description='Run flashcrash automatic trader')
parser.add_argument('--symbols', type=str, default='BTCUSD', help='symbols to trade (comma separated)')
parser.add_argument('--log-level', type=str, default='INFO', help='logging level for trader')
args = parser.parse_args()

lg = logging.getLogger()
lg.setLevel(args.log_level)
lg.handlers[0].setFormatter(logging.Formatter(fmt='%(asctime)-15s: %(levelname)-8s: %(message)s',
                                              datefmt='%Y-%m-%d %I:%M:%S'))

if '/' in args.symbols:
    with open(args.symbols) as f:
        symbols = f.read().splitlines()
else:
    symbols = args.symbols.split(',')

api = CoinAPI(symbols, data_types=['tickers'])
api.connect()
kill_queue = Queue()
workers = []
for s in symbols:
    w = FlashCoinTrader(api, s, kill_queue)
    w.start()
    workers.append(w)

while True:
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        for _ in workers:
            kill_queue.put(None)
        kill_queue.join()
        break
quit(0)
