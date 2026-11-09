from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, sample_frame
from src.models import Endpoint, IDLE, Tables, snapshot


def test_reverse_direction_conflict_leaves_no_partial_connection():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    before = snapshot(tables)

    # 第一方向所需的 T0[2] 空闲，反方向所需的 T0[5] 被 C1 占用。
    a, b = Endpoint(0, 5), Endpoint(0, 2)
    assert connect_pair('C2', a, b, tables) is False
    assert snapshot(tables) == before

    frame = sample_frame(0)
    output = exchange_frame(frame, tables)
    assert (output[1, 5], output[0, 1]) == (3, 116)
    assert (output[0, 2], output[0, 5]) == (IDLE, IDLE)

    assert disconnect_pair('C1', tables)
    assert connect_pair('C2', a, b, tables)
    output = exchange_frame(frame, tables)
    assert (output[0, 2], output[0, 5]) == (15, 6)
    assert (output[1, 5], output[0, 1]) == (IDLE, IDLE)
