import pytest
from copy import deepcopy
from src.models import Endpoint as E, Tables, snapshot
from src.connections import connect_pair, disconnect_pair

def test_internal_t_blocking_and_repeat_release():
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t) is True
    before = deepcopy(t)
    # (0,2)与(0,5)端点都空闲，但两个方向都要占用T0的输出TS5
    assert connect_pair('C2', E(0, 2), E(0, 5), t) is False
    assert snapshot(t) == snapshot(before)
    assert disconnect_pair('C1', t) is True
    assert disconnect_pair('C1', t) is False
    assert snapshot(t) == snapshot(Tables())
