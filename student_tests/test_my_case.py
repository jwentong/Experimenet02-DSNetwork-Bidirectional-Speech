"""依据REPORT.md中先写出的输入与预期验证交换和资源边界。"""
from copy import deepcopy

import numpy as np
import pytest

from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, run_frames, sample_frame
from src.models import Endpoint, IDLE, RESERVED, Tables
from src.s_switch import s_switch
from src.t_switch import t_switch


def test_manual_t_byte_swap():
    frame = np.arange(32, dtype=np.uint8)
    frame[1], frame[3] = 11, 33
    before = frame.copy()
    output = t_switch(frame, {1: 3, 3: 1})
    assert output[1] == 33 and output[3] == 11
    assert output[2] == IDLE
    assert np.array_equal(output[[0, 16]], frame[[0, 16]])
    assert np.array_equal(frame, before)
    assert not np.shares_memory(output, frame)


def test_manual_s_same_slot_swap():
    frames = sample_frame(0)
    before = frames.copy()
    output = s_switch(frames, {(0, 3): 1, (1, 3): 0})
    assert output[0, 3] == 110 and output[1, 3] == 9
    assert output[0, 1] == IDLE and output[1, 5] == IDLE
    assert np.array_equal(output[:, [0, 16]], frames[:, [0, 16]])
    assert np.array_equal(frames, before)
    assert not np.shares_memory(output, frames)


def test_two_pairs_match_manual_bytes_and_one_frame_delay():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    assert connect_pair('C2', Endpoint(0, 2), Endpoint(1, 6), tables)
    frames = [sample_frame(k) for k in range(4)]
    records = run_frames(frames, tables)
    first = records[0]['output']
    assert (int(first[1, 5]), int(first[0, 1]),
            int(first[1, 6]), int(first[0, 2])) == (3, 116, 6, 119)
    for k, record in enumerate(records):
        assert record['input_frame_id'] == k
        assert record['available_frame_id'] == k + 1
        for source, destination in ((Endpoint(0, 1), Endpoint(1, 5)),
                                    (Endpoint(1, 5), Endpoint(0, 1)),
                                    (Endpoint(0, 2), Endpoint(1, 6)),
                                    (Endpoint(1, 6), Endpoint(0, 2))):
            assert record['output'][destination.link_id, destination.timeslot] == (
                frames[k][source.link_id, source.timeslot])


def test_reverse_t_conflict_does_not_leave_forward_mapping():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    before = deepcopy(tables)
    # (0,5)->(0,2)的T0[2]可用，反向所需T0[5]被C1占用。
    assert connect_pair('blocked', Endpoint(0, 5), Endpoint(0, 2), tables) is False
    assert tables == before
    assert 2 not in tables.t_maps[0]
    frames = sample_frame(2)
    output = exchange_frame(frames, tables)
    assert output[1, 5] == frames[0, 1]
    assert output[0, 1] == frames[1, 5]


@pytest.mark.parametrize('blocked_output', [(1, 6), (0, 2)])
def test_s_only_conflict_is_atomic_in_either_direction(blocked_output):
    tables = Tables()
    tables.s_map[blocked_output] = 1
    before = deepcopy(tables)
    assert connect_pair('blocked', Endpoint(0, 2), Endpoint(1, 6), tables) is False
    assert tables == before
    assert tables.t_maps == [{}, {}]


def test_identical_existing_t_mapping_is_not_shared():
    tables = Tables()
    tables.t_maps[0][5] = 1
    before = deepcopy(tables)
    assert connect_pair('blocked', Endpoint(0, 1), Endpoint(1, 5), tables) is False
    assert tables == before


@pytest.mark.parametrize('byte', [0, 0xD5, 255])
def test_payload_value_does_not_determine_resource_occupancy(byte):
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    frames = sample_frame(0)
    frames[0, 1] = frames[1, 5] = byte
    before_frames = frames.copy()
    before_tables = deepcopy(tables)
    output = exchange_frame(frames, tables)
    assert output[1, 5] == byte and output[0, 1] == byte
    assert connect_pair('busy', Endpoint(0, 1), Endpoint(1, 6), tables) is False
    assert tables == before_tables
    assert np.array_equal(frames, before_frames)


def test_release_survivor_repeat_and_reconnect_same_id():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    assert connect_pair('C2', Endpoint(0, 2), Endpoint(1, 6), tables)
    assert disconnect_pair('C1', tables) is True
    assert tables.t_maps == [{6: 2}, {2: 6}]
    assert tables.s_map == {(1, 6): 0, (0, 2): 1}
    assert set(tables.pairs) == {'C2'}
    frames = sample_frame(1)
    output = exchange_frame(frames, tables)
    assert output[0, 1] == IDLE and output[1, 5] == IDLE
    assert output[1, 6] == frames[0, 2] and output[0, 2] == frames[1, 6]
    before = deepcopy(tables)
    assert disconnect_pair('C1', tables) is False
    assert disconnect_pair('missing', tables) is False
    assert tables == before
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables) is True
    restored = exchange_frame(frames, tables)
    assert restored[1, 5] == frames[0, 1] and restored[0, 1] == frames[1, 5]
    assert restored[1, 6] == frames[0, 2] and restored[0, 2] == frames[1, 6]


def test_released_internal_resource_can_use_different_endpoints():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    assert connect_pair('blocked', Endpoint(0, 2), Endpoint(0, 5), tables) is False
    assert disconnect_pair('C1', tables)
    assert connect_pair('new', Endpoint(0, 2), Endpoint(0, 5), tables)
    frames = sample_frame(0)
    output = exchange_frame(frames, tables)
    assert output[0, 5] == frames[0, 2] and output[0, 2] == frames[0, 5]


def test_equal_timeslots_on_different_links_are_distinct_endpoints():
    tables = Tables()
    assert connect_pair('equal-slot', Endpoint(0, 31), Endpoint(1, 31), tables)
    frames = sample_frame(3)
    output = exchange_frame(frames, tables)
    assert output[0, 31] == frames[1, 31]
    assert output[1, 31] == frames[0, 31]
    assert disconnect_pair('equal-slot', tables)
    assert tables == Tables()


@pytest.mark.parametrize('endpoint', [Endpoint(-1, 1), Endpoint(2, 1),
                                     Endpoint(0, -1), Endpoint(0, 32),
                                     Endpoint(0, 0), Endpoint(1, 16),
                                     Endpoint(0.0, 3), Endpoint(0, 2.5),
                                     Endpoint(0, 2.0), Endpoint(0, '2'),
                                     Endpoint(True, 3), Endpoint(0, True)])
def test_invalid_endpoint_preserves_existing_pair(endpoint):
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    before = deepcopy(tables)
    with pytest.raises(ValueError):
        connect_pair('invalid', Endpoint(0, 2), endpoint, tables)
    assert tables == before


@pytest.mark.parametrize('mapping', [{1: 0}, {16: 1}, {-1: 1}, {1: 32},
                                   {1.5: 2}, {1: '2'}, {True: 2}])
def test_invalid_t_mapping_leaves_input_unchanged(mapping):
    frame = sample_frame(0)[0]
    before = frame.copy()
    with pytest.raises(ValueError):
        t_switch(frame, mapping)
    assert np.array_equal(frame, before)


@pytest.mark.parametrize('mapping', [{(0, 0): 1}, {(1, 16): 0},
                                   {(-1, 1): 0}, {(0, -1): 1},
                                   {(0, 1): -1}, {(0, 32): 0},
                                   {(0, 1): 0.5}, {(True, 1): 0},
                                   {(0, 1.5): 1}, {(0,): 1}])
def test_invalid_s_mapping_leaves_input_unchanged(mapping):
    frames = sample_frame(0)
    before = frames.copy()
    with pytest.raises(ValueError):
        s_switch(frames, mapping)
    assert np.array_equal(frames, before)


@pytest.mark.parametrize('shape,dtype', [((31,), np.uint8), ((2, 32), np.uint8),
                                       ((32,), np.int16)])
def test_t_requires_uint8_frame_with_exact_shape(shape, dtype):
    frame = np.zeros(shape, dtype=dtype)
    with pytest.raises(ValueError):
        t_switch(frame, {})
    assert not frame.any()


@pytest.mark.parametrize('shape,dtype', [((32,), np.uint8), ((2, 31), np.uint8),
                                       ((2, 32), np.int16)])
def test_s_requires_uint8_frames_with_exact_shape(shape, dtype):
    frames = np.zeros(shape, dtype=dtype)
    with pytest.raises(ValueError):
        s_switch(frames, {})
    assert not frames.any()


def test_empty_tables_preserve_only_reserved_slots_on_each_link():
    frames = sample_frame(1)
    output = exchange_frame(frames, Tables())
    for slot in range(32):
        if slot in RESERVED:
            assert np.array_equal(output[:, slot], frames[:, slot])
        else:
            assert np.all(output[:, slot] == IDLE)
