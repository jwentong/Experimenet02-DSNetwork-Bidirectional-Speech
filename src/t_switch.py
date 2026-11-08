"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    if (not isinstance(input_frame, np.ndarray)
            or input_frame.shape != (SLOTS,)
            or input_frame.dtype != np.uint8):
        raise ValueError('T输入必须是uint8[32]数组')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[slot] = input_frame[slot]

    for out_ts, in_ts in control_memory.items():
        for slot in (out_ts, in_ts):
            if (not isinstance(slot, (int, np.integer))
                    or isinstance(slot, (bool, np.bool_))
                    or slot not in range(SLOTS) or slot in RESERVED):
                raise ValueError('T映射必须使用合法业务时隙')
        output[out_ts] = input_frame[in_ts]
    return output
