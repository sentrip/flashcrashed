from threading import Thread
from _thread import interrupt_main
import pytest
import time
from flashcrashed.cli import main


def test_main(patched_bitfinex):
    trader, notifier = patched_bitfinex

    def wait_sell():
        while len(trader.calls) < 2:
            time.sleep(0.01)
        interrupt_main()

    Thread(target=wait_sell).start()
    with pytest.raises(SystemExit):
        main(['key', 'secret'])

    assert trader.calls == [('BUY', 1), ('SELL', 1)]
    assert notifier.calls[0][1]['body'].startswith('BTCUSD was BOUGHT'), \
        "Incorrect notification message"
    assert notifier.calls[1][1]['body'].startswith('BTCUSD was SOLD'), \
        "Incorrect notification message"
