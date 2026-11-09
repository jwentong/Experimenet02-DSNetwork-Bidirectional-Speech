from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, sample_frame
from src.models import IDLE, Endpoint, Tables


def test_reverse_route_internal_block_and_release():
    tables = Tables()
    a, b = Endpoint(0, 1), Endpoint(1, 5)
    assert connect_pair('C1', a, b, tables)

    # 新端点空闲，但请求需要已占用的T0输出TS5，因此必须整体拒绝。
    assert not connect_pair('blocked', Endpoint(0, 2), Endpoint(0, 5), tables)

    frame = sample_frame(2)
    output = exchange_frame(frame, tables)
    assert output[1, 5] == frame[0, 1]
    assert output[0, 1] == frame[1, 5]

    assert disconnect_pair('C1', tables)
    released = exchange_frame(frame, tables)
    assert released[1, 5] == IDLE
    assert released[0, 1] == IDLE
    assert not disconnect_pair('C1', tables)
