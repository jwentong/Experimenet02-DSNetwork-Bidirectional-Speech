"""自拟反例：内部阻塞、IDLE字节不释放端点、释放后重用。"""
from src.models import Endpoint, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def _table_copy(t):
    return (dict(t.t_maps[0]), dict(t.t_maps[1]), dict(t.s_map), dict(t.pairs))


def test_internal_blocking_keeps_tables_unchanged():
    t = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), t) is True
    before = _table_copy(t)
    # (0,2)与(0,5)两个端点都空闲，但两个方向都必须写T0的输出TS5，构成内部T阻塞
    assert connect_pair('C2', Endpoint(0, 2), Endpoint(0, 5), t) is False
    assert _table_copy(t) == before  # 拒绝后整张控制表保持原样
    x = sample_frame(3)
    y = exchange_frame(x, t)
    assert y[1, 5] == x[0, 1] and y[0, 1] == x[1, 5]  # C1两个方向继续传送


def test_idle_byte_does_not_free_endpoint_and_release_reuse():
    t = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), t) is True
    x = sample_frame(0)
    x[0, 1] = IDLE
    y = exchange_frame(x, t)
    assert y[1, 5] == IDLE  # 收到IDLE字节不代表端口空闲
    assert connect_pair('C2', Endpoint(0, 1), Endpoint(1, 6), t) is False  # 端点仍被占用
    assert disconnect_pair('C1', t) is True
    assert disconnect_pair('C1', t) is False  # 重复释放
    assert connect_pair('C2', Endpoint(0, 1), Endpoint(1, 6), t) is True  # 资源可重新使用
    z = exchange_frame(sample_frame(1), t)
    assert z[1, 6] == sample_frame(1)[0, 1]
