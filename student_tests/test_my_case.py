import numpy as np
from src.t_switch import t_switch
from src.models import IDLE

def test_my_case():
    inp = np.array([0, 11, 0, 33] + [0]*28, dtype=np.uint8)
    cm = {1:3, 3:1}
    out = t_switch(inp, cm)
    assert out[1] == 33
    assert out[3] == 11
    assert out[2] == IDLE
