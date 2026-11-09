"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    for out_slot, in_slot in control_memory.items():
        if not (0 <= out_slot < SLOTS) or not (0 <= in_slot < SLOTS):
            raise ValueError('映射时隙必须在0到31之间')
        if out_slot in RESERVED or in_slot in RESERVED:
            raise ValueError('保留时隙TS0/TS16不能出现在映射中')
    out = np.full(SLOTS, IDLE, dtype=np.uint8)
    out[0] = input_frame[0]
    out[16] = input_frame[16]
    for out_slot, in_slot in control_memory.items():
        out[out_slot] = input_frame[in_slot]
    return out
