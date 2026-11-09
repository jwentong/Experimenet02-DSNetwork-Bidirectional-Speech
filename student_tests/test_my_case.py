"""自拟反例：内部阻塞、双向字节传送与释放重用。"""
from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_internal_blocking_keeps_original_transfer():
    # 输入与预期：C1 连接 A=(0,1)、B=(1,5) 后，再请求 (0,2) 与 (0,5)。
    # 虽然 (0,2)、(0,5) 都不是已占端点，但方向 (0,2)->(0,5) 需要 T0 的输出 TS5，
    # 与 C1 已用的 T0[5]=1 冲突，属固定 T->S 路径的内部阻塞，必须整体拒绝且原表不变。
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t) is True
    before = (dict(t.t_maps[0]), dict(t.t_maps[1]), dict(t.s_map), dict(t.pairs))
    assert connect_pair('blocked', E(0, 2), E(0, 5), t) is False
    after = (dict(t.t_maps[0]), dict(t.t_maps[1]), dict(t.s_map), dict(t.pairs))
    assert after == before, '拒绝后控制表必须保持不变'
    # 原连接仍能双向传送字节
    x = sample_frame(0)
    y = exchange_frame(x, t)
    assert int(y[1, 5]) == int(x[0, 1])  # A -> B
    assert int(y[0, 1]) == int(x[1, 5])  # B -> A


def test_release_then_reuse_same_resources():
    # 输入与预期：释放 C1 后，其端点 (0,1)、(1,5) 及内部 T/S 表项全部归还，
    # 输出自然回到 IDLE，相同端点应能再次建立连接。
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t) is True
    assert disconnect_pair('C1', t) is True
    x = sample_frame()
    y = exchange_frame(x, t)
    assert int(y[0, 1]) == IDLE and int(y[1, 5]) == IDLE
    assert connect_pair('C2', E(0, 1), E(1, 5), t) is True
