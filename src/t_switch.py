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

    for output_ts, input_ts in control_memory.items():
        for slot in (output_ts, input_ts):
            if not isinstance(slot, Integral) or isinstance(slot, bool):
                raise ValueError(f'时隙号必须是整数：{slot!r}')
            if slot not in range(SLOTS) or slot in RESERVED:
                raise ValueError(f'T交换需要合法的业务时隙：{slot}')
        output_frame[output_ts] = input_frame[input_ts]

    return output_frame
