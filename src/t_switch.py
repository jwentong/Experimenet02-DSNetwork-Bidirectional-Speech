"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _valid_slot(slot):
    return (
        isinstance(slot, (int, np.integer))
        and not isinstance(slot, bool)
        and 0 <= int(slot) < SLOTS
        and int(slot) not in RESERVED
    )


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,) or frame.dtype != np.uint8:
        raise ValueError('input_frame must be a uint8 array with 32 samples')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    output[0] = frame[0]
    output[16] = frame[16]

    for out_slot, in_slot in control_memory.items():
        if not _valid_slot(out_slot) or not _valid_slot(in_slot):
            raise ValueError('control mapping must use business timeslots TS1-TS31, excluding TS16')
        output[int(out_slot)] = frame[int(in_slot)]

    return output
