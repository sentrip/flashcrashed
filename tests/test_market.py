from flashcrashed.market.gen import FlashedMarket


def test_crash_always_occurs(market_maker):
    for _ in range(50):
        market = FlashedMarket(market_maker())
        prices = []
        for price in market:
            prices.append(price)
        assert market.crashes, 'No flashcrashes occured in single run of flashedmarket, %d' % len(prices)
        assert min(prices) < sum(prices) / len(prices) / 3, 'Flashcrash did not have magnitude of 3 or higher'
        for crash in market.crashes:
            assert crash['ratio'] >= 3


def test_single_episode(env):
    prices = [env.reset()]
    done = False
    while not done:
        price, r, done, _ = env.step(1)
        prices.append(price)
        assert r == 0, "Got non-zero reward for doing nothing"
    assert min(prices) < sum(prices) / len(prices) / 3, \
        'Flashcrash did not occur in gym'


def test_positive_buy_reward(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    while not done:
        action = 1
        if env.market.crash_start < env.market.position <= env.market.crash_end + 10:
            count += 1
            if count > env.market.drop_duration - 1 and not bought:
                action = 0
                bought = True
        price, r, done, _ = env.step(action)
        prices.append(price)
        if action == 1:
            assert r == 0, "Got non-zero reward for doing nothing"
        elif action == 0:
            assert r == 1, \
                "Did not get perfect reward for buying in middle of flashcrash"
    assert bought, "Did not buy"


def test_negative_buy_reward(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    price, r, _, _ = env.step(0)
    prices.append(price)
    assert r < 0, 'Did not get negative reward for buying outside of flashcrash'
    while not done:
        action = 1
        if env.market.crashing:
            count += 1
        if count > env.market.drop_duration - 1:
            action = 0
        price, r, done, _ = env.step(action)
        prices.append(price)
        if action == 1:
            assert r == 0, "Got non-zero reward for doing nothing"
        elif action == 0:
            if not bought or not env.bought:
                bought = True
                assert 1 == r, "Did not get perfect reward for buying in middle of flashcrash"
            else:
                assert r < 0, "Did not get negative reward for buying multiple times"
                done = True


def test_positive_sell_reward(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    sold = False
    while not done:
        action = 1
        if env.market.crashing:
            count += 1
            if count > env.market.drop_duration - 1 and not bought:
                action = 0
                bought = True
        if env.market.returned and not sold:
            sold = True
            action = 2
        price, r, done, _ = env.step(action)
        prices.append(price)
        if action == 1:
            assert r == 0, "Got non-zero reward for doing nothing"
        elif action == 2:
            assert r == 1, "Did not get perfect reward for selling after flashcrash"


def test_negative_sell_reward(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    sold = False
    price, r, _, _ = env.step(2)
    prices.append(price)
    assert r < 0, 'Did not get negative reward for selling outside of flashcrash'
    price, r, _, _ = env.step(0)
    prices.append(price)
    price, r, _, _ = env.step(2)
    prices.append(price)
    assert r < 0, 'Did not get negative reward for selling outside of flashcrash'
    price, r, _, _ = env.step(2)
    prices.append(price)
    assert r < 0, 'Did not get negative reward for selling outside of flashcrash'
    while not done:
        action = 1
        if env.market.crashing:
            count += 1
            if count > env.market.drop_duration - 1 and not bought:
                action = 0
                bought = True
        if env.market.returned:
            action = 2
        price, r, done, _ = env.step(action)
        prices.append(price)
        if action == 1:
            assert r == 0, "Got non-zero reward for doing nothing"
        elif action == 2:
            if not sold:
                sold = True
                assert r == 1, "Did not get perfect reward for selling after flashcrash"
            else:
                assert r < 0, "Did not get negative reward for selling multiple times"


def test_crash_update_when_buy_sell(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    sold = False
    while not done:
        action = 1
        if env.market.crashing:
            count += 1
            if count > env.market.drop_duration - 1 and not bought:
                action = 0
                bought = True
        if env.market.rising and not sold:
            sold = True
            action = 2
        price, r, done, _ = env.step(action)
        prices.append(price)
    for crash in [env.market.crashes[0]]:
        assert crash['bought'], 'Did not add buy to crash details when bought successfully'
        assert crash['sold'], 'Did not add sell to crash details when sold successfully'


def test_crash_update_when_no_buy_sell(env):
    prices = [env.reset()]
    done = False
    sold = False
    while not done:
        action = 1
        if env.market.returned and not sold:
            sold = True
            action = 2
        price, r, done, _ = env.step(action)
        prices.append(price)
    for crash in [env.market.crashes[0]]:
        assert not crash['sold'], 'Added sell to crash details when sold after not buying'


def test_crash_update_when_buy_no_sell(env):
    prices = [env.reset()]
    done = False
    count = 0
    bought = False
    while not done:
        action = 1
        if env.market.crashing:
            count += 1
            if count > env.market.drop_duration - 1 and not bought:
                action = 0
                bought = True
        price, r, done, _ = env.step(action)
        prices.append(price)
    for crash in [env.market.crashes[0]]:
        assert crash['bought'], 'Did not add buy to crash details when bought successfully'

