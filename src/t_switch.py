"""任务一：同一链路的时间交换。"""
import numbers

import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _business_slot(value):
    if not isinstance(value, numbers.Integral):
        raise ValueError('时隙必须为整数')
    value = int(value)
    if value not in range(SLOTS) or value in RESERVED:
        raise ValueError('映射必须使用0~31范围内的业务时隙（不含TS0/TS16）')
    return value


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError('输入帧必须为长度32的数组')
    frame = frame.astype(np.uint8, copy=False)

    # Validate the complete control table before producing any mapped output.
    mappings = [(_business_slot(out_slot), _business_slot(in_slot))
                for out_slot, in_slot in control_memory.items()]

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[slot] = frame[slot]
    for out_slot, in_slot in mappings:
        output[out_slot] = frame[in_slot]
    return output
