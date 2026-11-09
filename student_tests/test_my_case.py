from src.models import Endpoint as E, Tables
from src.connections import connect_pair, disconnect_pair


def test_reuse_after_release():
    t = Tables()
    assert connect_pair('A', E(0, 1), E(1, 5), t)
    assert disconnect_pair('A', t)
    assert connect_pair('B', E(0, 1), E(1, 5), t)
    assert t.pairs['B'] == (E(0, 1), E(1, 5))


def test_internal_conflict_is_rejected():
    t = Tables()
    assert connect_pair('A', E(0, 1), E(1, 5), t)
    assert connect_pair('B', E(0, 2), E(0, 5), t) is False
    assert t.pairs.keys() == {'A'}
