"""任务一：同一链路的时间交换。"""
from numbers import Integral

import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    output_frame = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output_frame[slot] = input_frame[slot]

    for output_slot, input_slot in control_memory.items():
        if any(
            not isinstance(slot, Integral)
            or isinstance(slot, bool)
            or not 0 <= slot < SLOTS
            or slot in RESERVED
            for slot in (output_slot, input_slot)
        ):
            raise ValueError("T 交换的输入和输出必须使用合法业务时隙")
        output_frame[output_slot] = input_frame[input_slot]
    return output_frame
