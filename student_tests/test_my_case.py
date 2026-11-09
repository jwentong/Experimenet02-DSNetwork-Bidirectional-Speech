import numpy as np
from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_internal_t_block_then_reuse():
    # C1 占用 (0,1)<->(1,5)；C2 端口不同，但 B->D 也需要 T0 的输出 TS5，内部阻塞。
    tables = Tables()
    a, b = E(0, 1), E(1, 5)
    c, d = E(0, 2), E(0, 5)
    assert connect_pair('C1', a, b, tables) is True
    before = exchange_frame(sample_frame(0), tables)
    assert connect_pair('C2', c, d, tables) is False
    # 被拒绝后原连接仍正常传送，表未受影响。
    after = exchange_frame(sample_frame(0), tables)
    assert np.array_equal(before, after)
    assert after[b.link_id, b.timeslot] == sample_frame(0)[a.link_id, a.timeslot]
    # 释放 C1 后，同一对端点可重新建立，且首次交换即按新表工作。
    assert disconnect_pair('C1', tables) is True
    assert connect_pair('C3', c, d, tables) is True
    frame = sample_frame(3)
    switched = exchange_frame(frame, tables)
    assert switched[d.link_id, d.timeslot] == frame[c.link_id, c.timeslot]
    assert switched[c.link_id, c.timeslot] == frame[d.link_id, d.timeslot]


def test_idle_byte_does_not_free_port():
    # 源字节恰为 IDLE 时，端口仍被占用，不能凭字节值判断空闲。
    tables = Tables()
    a, b = E(1, 7), E(0, 9)
    assert connect_pair('X', a, b, tables) is True
    frame = sample_frame(0)
    frame[a.link_id, a.timeslot] = IDLE
    out = exchange_frame(frame, tables)
    assert out[b.link_id, b.timeslot] == IDLE
    assert connect_pair('Y', a, E(0, 12), tables) is False
