"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _validate_slot(value, *, name):
    if not isinstance(value, (int, np.integer)) or isinstance(value, bool):
        raise ValueError(f'{name} 必须是合法的整数时隙')
    if int(value) not in range(SLOTS) or int(value) in RESERVED:
        raise ValueError(f'{name} 必须是业务时隙，且不能使用保留时隙')
    return int(value)


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame, dtype=np.uint8)
    if frame.shape != (SLOTS,):
        raise ValueError('input_frame 必须是长度为 32 的 uint8 数组')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in range(SLOTS):
        if slot in RESERVED:
            output[slot] = frame[slot]

    for out_slot, in_slot in control_memory.items():
        out_index = _validate_slot(out_slot, name='输出时隙')
        in_index = _validate_slot(in_slot, name='输入时隙')
        output[out_index] = frame[in_index]

    return output.astype(np.uint8, copy=False)
