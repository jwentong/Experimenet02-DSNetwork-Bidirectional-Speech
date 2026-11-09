"""补充验证内部阻塞、反方向冲突及跨链路同号时隙。"""
from copy import deepcopy

from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, sample_frame


def test_internal_block_release_and_reuse():
    tables = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), tables)
    assert connect_pair('C2', E(0, 2), E(1, 6), tables)
    before = deepcopy(tables)
    # 两端均空闲，但正方向需要已被C1占用的T0[5]。
    assert connect_pair('blocked', E(0, 3), E(0, 5), tables) is False
    assert tables == before
    frame = sample_frame(3)
    output = exchange_frame(frame, tables)
    assert output[1, 5] == frame[0, 1]
    assert output[0, 1] == frame[1, 5]
    assert disconnect_pair('C1', tables)
    output = exchange_frame(frame, tables)
    assert output[0, 1] == IDLE and output[1, 5] == IDLE
    assert output[1, 6] == frame[0, 2] and output[0, 2] == frame[1, 6]
    assert connect_pair('reused', E(0, 3), E(0, 5), tables)
    output = exchange_frame(frame, tables)
    assert output[0, 5] == frame[0, 3] and output[0, 3] == frame[0, 5]


def test_reverse_direction_s_conflict_is_atomic():
    tables = Tables()
    # 预留反方向的S输出，正方向资源均空闲。
    tables.s_map[(0, 4)] = 0
    before = deepcopy(tables)
    assert connect_pair('rejected', E(0, 4), E(1, 8), tables) is False
    assert tables == before


def test_equal_timeslots_on_distinct_links_are_independent():
    tables = Tables()
    assert connect_pair('left', E(0, 7), E(0, 8), tables)
    assert connect_pair('right', E(1, 7), E(1, 8), tables)
    frame = sample_frame(1)
    frame[0, 7] = IDLE
    output = exchange_frame(frame, tables)
    assert output[0, 8] == IDLE
    assert output[0, 7] == frame[0, 8]
    assert output[1, 8] == frame[1, 7]
    assert output[1, 7] == frame[1, 8]
    before = deepcopy(tables)
    assert connect_pair('busy', E(0, 7), E(1, 9), tables) is False
    assert tables == before
    assert disconnect_pair('left', tables)
    output = exchange_frame(frame, tables)
    assert output[0, 7] == IDLE and output[0, 8] == IDLE
    assert output[1, 8] == frame[1, 7] and output[1, 7] == frame[1, 8]
