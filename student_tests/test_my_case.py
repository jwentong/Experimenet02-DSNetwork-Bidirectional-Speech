"""自拟反例：验证内部T输出阻塞被整体拒绝，以及释放后资源可重用。"""
from copy import deepcopy
from src.models import Endpoint as E, Tables
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_internal_t_blocking_atomic():
    # C1占用A=(0,1)、B=(1,5)，已写入T0[5]=1
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t)
    old = deepcopy(t)
    # 新端点(0,2)与(0,5)未被C1占用，但方向(0,2)->(0,5)同样需要T0的输出TS5
    assert connect_pair('blocked', E(0, 2), E(0, 5), t) is False
    assert t == old


def test_release_then_reuse():
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t)
    assert disconnect_pair('C1', t)
    # 释放后同一端点资源可被新连接重用
    assert connect_pair('C2', E(0, 1), E(1, 5), t)
    x = sample_frame(3)
    y = exchange_frame(x, t)
    assert y[1, 5] == x[0, 1] and y[0, 1] == x[1, 5]
