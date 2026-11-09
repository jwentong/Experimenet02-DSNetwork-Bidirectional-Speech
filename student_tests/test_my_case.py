"""自拟反例：同链路双向、内部T输出争用整体拒绝、IDLE字节不释放端口、释放后可重用。

手算依据见REPORT.md“反例与验证”一节。
"""
from copy import deepcopy

import numpy as np

from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_same_link_bidirectional_tables_and_transfer():
    """同链路(0,4)-(0,9)：T0[9]=4、T0[4]=9，S两端都指向链路0，时隙号不变。"""
    t = Tables()
    assert connect_pair('same', E(0, 4), E(0, 9), t) is True
    assert t.t_maps[0] == {9: 4, 4: 9} and t.t_maps[1] == {}
    assert t.s_map == {(0, 9): 0, (0, 4): 0}

    x = sample_frame(3)
    y = exchange_frame(x, t)
    assert y[0, 9] == x[0, 4] and y[0, 4] == x[0, 9]
    # 未连接的同链路业务时隙仍回到IDLE，不受本次连接影响
    assert y[0, 5] == IDLE and y[1, 5] == IDLE


def test_internal_t_conflict_rejects_whole_request():
    """(0,2)-(0,5)的正向需要T0[5]，与C1的T0[5]=1争用同一内部T输出，必须整体拒绝。"""
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t)
    before = deepcopy(t)

    assert connect_pair('C2', E(0, 2), E(0, 5), t) is False
    assert t == before
    # 端点(0,2)没有被占用，失败原因是内部T输出(0,5)而非用户忙
    assert t.t_maps[0] == {5: 1} and (0, 2) not in t.s_map

    # 拒绝后原连接继续传送
    x = sample_frame()
    y = exchange_frame(x, t)
    assert y[1, 5] == x[0, 1] and y[0, 1] == x[1, 5]


def test_idle_byte_is_not_a_free_endpoint():
    """数据字节恰好等于IDLE(0xD5)时，端点仍被占用，不能据此判定空闲。"""
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t)
    x = sample_frame(1).copy()
    x[0, 1] = IDLE
    y = exchange_frame(x, t)
    assert y[1, 5] == IDLE  # 传送的是空闲字节，而不是没有连接

    assert connect_pair('C2', E(0, 1), E(1, 6), t) is False
    assert set(t.pairs) == {'C1'} and (1, 6) not in t.s_map


def test_release_clears_both_directions_then_reuses():
    """释放后T/S两组表项都清除，资源可被新连接重新建立，重复释放返回False。"""
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t)
    assert connect_pair('C2', E(0, 2), E(1, 6), t)
    assert disconnect_pair('C1', t) is True
    assert t.t_maps == [{6: 2}, {2: 6}] and t.s_map == {(1, 6): 0, (0, 2): 1}

    assert disconnect_pair('C1', t) is False  # 重复释放不影响C2
    assert t.t_maps == [{6: 2}, {2: 6}] and set(t.pairs) == {'C2'}

    assert connect_pair('C3', E(0, 1), E(1, 5), t) is True
    x = sample_frame(0)
    y = exchange_frame(x, t)
    assert y[1, 5] == x[0, 1] and y[0, 1] == x[1, 5]
    assert y[1, 6] == x[0, 2] and y[0, 2] == x[1, 6]
