import random


def test_action_always_correct(detector):
    detector.reset()
    actions = set()
    for _ in range(50000):
        a = detector.predict(random.random() * 100000)
        actions.add(a)
        assert a in {0, 1, 2}, "Action not an integer between 0 and 2"
    assert len(actions) == 3, 'Did not commit all actions, %s' % str(actions)


def test_action_never_same(detector):
    last = -1
    detector.reset()
    actions = set()
    for _ in range(50000):
        a = detector.predict(random.random() * 100000)
        actions.add(a)
        if a != 1:
            assert a != last, "Wanted to {} more than once in a row".format(['BUY', 'SELL'][max(a-1, 0)])
            last = a
    assert len(actions) == 3, 'Did not commit all actions, %s' % str(actions)
