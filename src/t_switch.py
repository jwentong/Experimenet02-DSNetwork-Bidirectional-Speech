"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,) or frame.dtype != np.uint8:
        raise ValueError('input_frame must be a uint8 array with 32 slots')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    output[list(RESERVED)] = frame[list(RESERVED)]

    for output_slot, input_slot in control_memory.items():
        if (not isinstance(output_slot, (int, np.integer))
                or not isinstance(input_slot, (int, np.integer))
                or output_slot not in range(SLOTS)
                or input_slot not in range(SLOTS)
                or output_slot in RESERVED
                or input_slot in RESERVED):
            raise ValueError('T mappings must use valid business timeslots')
        output[output_slot] = frame[input_slot]

    return output
