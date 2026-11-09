"""自拟测试：验证 T/S 交换与双向连接、释放的关键规则。"""
import numpy as np
from src.models import IDLE, Endpoint, Tables
from src.t_switch import t_switch
from src.s_switch import s_switch
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_t_switch_reserved_and_mapping():
    """T 交换：保留时隙原位透传，控制表按输出→输入映射，未连接填 IDLE。"""
    x = np.arange(32, dtype=np.uint8)
    y = t_switch(x, {5: 2})
    assert y[0] == 0 and y[16] == 16      # TS0/TS16 原位透传
    assert y[5] == 2                       # 输出时隙 5 取输入时隙 2
    assert y[7] == IDLE                    # 未连接业务填空闲


def test_s_switch_keeps_slot():
    """S 交换：只改链路、时隙不变；保留时隙沿本链路透传。"""
    x = sample_frame(0)
    y = s_switch(x, {(0, 4): 1})
    assert y[0, 4] == x[1, 4]              # 链路 1 的 TS4 送到链路 0 的 TS4
    assert y[0, 0] == x[0, 0]              # 保留时隙透传


def test_bidirectional_and_release():
    """双向连接后 A/B 字节互通；释放后两端回到 IDLE。"""
    t = Tables()
    a, b = Endpoint(0, 1), Endpoint(1, 5)
    assert connect_pair('X', a, b, t)
    x = sample_frame(0)
    y = exchange_frame(x, t)
    assert y[1, 5] == x[0, 1] and y[0, 1] == x[1, 5]
    assert disconnect_pair('X', t)
    y2 = exchange_frame(x, t)
    assert y2[1, 5] == IDLE and y2[0, 1] == IDLE
