from src.t_switch import t_switch
from src.s_switch import s_switch
import numpy as np

def test_my_custom_case():
    # 测试 T 交换：输入 TS1 为 11，TS3 为 33，交换它们
    frame = np.full(32, 0xD5, dtype=np.uint8)
    frame[1] = 11
    frame[3] = 33
    out = t_switch(frame, {1: 3, 3: 1})
    assert int(out[1]) == 33
    assert int(out[3]) == 11
    assert int(out[2]) == 0xD5 # 没连的应该是 IDLE

    # 测试 S 交换：输出链路0的 TS3 取输入链路1的 TS3
    frames = np.full((2, 32), 0xD5, dtype=np.uint8)
    frames[1, 3] = 77
    out_s = s_switch(frames, {(0, 3): 1})
    assert int(out_s[0, 3]) == 77
    assert int(out_s[0, 1]) == 0xD5