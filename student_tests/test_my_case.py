import numpy as np
from src.models import Endpoint, Tables
from src.t_switch import t_switch
from src.s_switch import s_switch
from src.connections import connect_pair, disconnect_pair

def test_my_internal_blocking_and_switch_case():
    frame = np.arange(32, dtype=np.uint8)
    t_out = t_switch(frame, {1: 3, 3: 1})
    assert int(t_out[1]) == 3 and int(t_out[3]) == 1
    frames = np.vstack([frame, frame + 100]).astype(np.uint8)
    s_out = s_switch(frames, {(0, 3): 1})
    assert int(s_out[0, 3]) == int(frames[1, 3])
    tables = Tables()
    assert connect_pair('C1', Endpoint(0, 1), Endpoint(1, 5), tables) is True
    assert connect_pair('C_conflict', Endpoint(0, 2), Endpoint(0, 5), tables) is False
    assert tables.t_maps[0] == {5: 1}
    assert disconnect_pair('C1', tables) is True
    assert connect_pair('C_reuse', Endpoint(0, 2), Endpoint(0, 5), tables) is True
