from copy import deepcopy

from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, sample_frame
from src.models import Endpoint, IDLE, Tables


def test_second_direction_conflict_is_atomic_and_resources_can_be_reused():
    tables = Tables()
    assert connect_pair("C1", Endpoint(0, 1), Endpoint(1, 5), tables)
    before = deepcopy(tables)
    endpoint_e = Endpoint(0, 5)
    endpoint_f = Endpoint(0, 2)

    # E -> F is free, but F -> E would overwrite C1's T0[5].
    assert connect_pair("C3", endpoint_e, endpoint_f, tables) is False
    assert tables == before
    frame = sample_frame(0)
    output = exchange_frame(frame, tables)
    assert (output[0, 1], output[1, 5]) == (116, 3)
    assert (output[0, 5], output[0, 2]) == (IDLE, IDLE)

    assert disconnect_pair("C1", tables)
    assert connect_pair("C3", endpoint_e, endpoint_f, tables)
    output = exchange_frame(frame, tables)
    assert (output[0, 5], output[0, 2]) == (6, 15)
