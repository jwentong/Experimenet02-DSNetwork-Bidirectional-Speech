import numpy as np
from src.t_switch import t_switch, IDLE

def test_my_t_switch_case():
    # 自己的T交换测试场景
    frame_in = np.array([i for i in range(32)], dtype=np.uint8)
    # 控制表：输出TS2取自输入TS7
    ctrl = {2:7}
    out = t_switch(frame_in, ctrl)
    assert out[0] == frame_in[0]    # TS0透传
    assert out[16] == frame_in[16]  # TS16透传
    assert out[2] == frame_in[7]
    assert out[5] == IDLE          # 未映射时隙等于IDLE
