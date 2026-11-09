from copy import deepcopy
import numpy as np
from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame

def test_internal_t_block_is_atomic_and_survivor_keeps_working():
    tables=Tables()
    a,b=E(0,1),E(1,5)
    assert connect_pair("C1",a,b,tables)
    before=deepcopy(tables)

    # 新端点未被C1占用，但(0,5)会再次占用T0的输出TS5，应判为内部阻塞。
    assert connect_pair("C2",E(0,2),E(0,5),tables) is False
    assert tables==before

    x=sample_frame(0)
    y=exchange_frame(x,tables)
    assert y[1,5]==x[0,1]==3
    assert y[0,1]==x[1,5]==116

    assert disconnect_pair("C1",tables)
    z=exchange_frame(x,tables)
    assert z[1,5]==IDLE and z[0,1]==IDLE
