"""学生自拟反例：内部T阻塞必须原子拒绝，释放后资源可重用。"""
from copy import deepcopy

import numpy as np

from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame
from src.models import Endpoint, IDLE, Tables
from src.s_switch import s_switch


def test_internal_t_conflict_atomic_and_reusable():
    """C1占用T0输出TS5；C2端点未占用但同样需要T0[5]，必须整体拒绝。"""
    tables = Tables()
    a, b = Endpoint(0, 1), Endpoint(1, 5)
    c, d = Endpoint(0, 2), Endpoint(0, 5)

    assert connect_pair('C1', a, b, tables) is True
    before = deepcopy(tables)

    assert connect_pair('C2', c, d, tables) is False
    assert tables == before

    assert disconnect_pair('C1', tables) is True
    assert connect_pair('C2', c, d, tables) is True
    assert tables.t_maps[0][5] == 2
    assert tables.s_map[(0, 5)] == 0


def test_s_switch_keeps_timeslot_and_fills_idle():
    """S只改变链路，不改变时隙；未连接位置填IDLE。"""
    frames = sample_frame(0)
    out = s_switch(frames, {(0, 3): 1})

    assert out[0, 3] == frames[1, 3]
    assert out[1, 3] == IDLE
    assert out[0, 0] == frames[0, 0]
    assert out[0, 16] == frames[0, 16]
    assert np.array_equal(frames, sample_frame(0))
