

def test_flashcrash_execution(trader, api):
    for _ in range(600):
        trader.on_price('BTCUSD', api.get('', '')['bid'])
    assert 2 == len(trader.trader.calls), 'Executed more than two trade calls'
    assert ('BUY', 1.0) in trader.trader.calls, 'Did not buy'
    assert ('SELL', 1.0) in trader.trader.calls, 'Did not sell'


def test_simultaneous_flashcrash_execution(trader, apis):
    for _ in range(600):
        for api, s in zip(apis, [str(i) for i in range(len(apis))]):
            trader.on_price(s, api.get('', '')['bid'])
    assert 2 == len(trader.trader.calls), 'Executed more than two trade calls'
    assert ('BUY', 1.0) in trader.trader.calls, 'Did not buy'
    assert ('SELL', 1.0) in trader.trader.calls, 'Did not sell'
