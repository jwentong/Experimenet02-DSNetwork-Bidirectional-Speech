import numpy as np

from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame
from src.models import Endpoint, Tables


def test_conflict_is_rejected_and_release_restores_idle():
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables)
    frame = sample_frame(3)
    out = exchange_frame(frame, tables)
    assert out[1, 5] == frame[0, 1]
    assert out[0, 1] == frame[1, 5]

    assert not connect_pair('conflict', Endpoint(0, 2), Endpoint(1, 5), tables)
    assert disconnect_pair('C1', tables)
    assert tables.t_maps == [{}, {}]
    assert tables.s_map == {}
    assert tables.pairs == {}

    new_frame = np.array([[10 + i for i in range(32)], [20 + i for i in range(32)]], dtype=np.uint8)
    result = exchange_frame(new_frame, tables)
    assert result[0, 1] == 0xD5
    assert result[1, 5] == 0xD5
