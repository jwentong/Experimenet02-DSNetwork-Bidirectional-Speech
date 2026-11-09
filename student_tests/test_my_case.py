from copy import deepcopy

from src.connections import connect_pair, disconnect_pair
from src.engine import run_frames, sample_frame
from src.models import Endpoint, IDLE, Tables


def test_idle_byte_does_not_mean_free_and_resource_can_be_reused():
    tables = Tables()
    a, b = Endpoint(0, 1), Endpoint(1, 5)
    assert connect_pair('first', a, b, tables)
    frame = sample_frame(0)
    frame[0, 1] = IDLE
    out = run_frames([frame], tables)[0]['output']
    assert out[1, 5] == IDLE
    before = deepcopy(tables)
    assert not connect_pair('second', a, Endpoint(1, 7), tables)
    assert tables == before
    assert disconnect_pair('first', tables)
    assert connect_pair('second', a, Endpoint(1, 7), tables)
    assert run_frames([frame], tables)[0]['output'][1, 7] == IDLE
