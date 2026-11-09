"""任务一：同一链路的时间交换。"""
from numbers import Integral

import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _is_business_slot(value):
    return (
        isinstance(value, Integral)
        and not isinstance(value, bool)
        and 0 <= value < SLOTS
        and value not in RESERVED
    )

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError(f'输入帧必须是长度为{SLOTS}的一维数组')
    frame = np.asarray(frame, dtype=np.uint8)

    try:
        mappings = list(control_memory.items())
    except (AttributeError, TypeError) as exc:
        raise ValueError('T控制表必须是输出时隙到输入时隙的映射') from exc

    # 先完整校验，保证出错时不会返回修改了一半的帧。
    for output_slot, input_slot in mappings:
        if not _is_business_slot(output_slot) or not _is_business_slot(input_slot):
            raise ValueError('T控制表只能映射合法业务时隙，不能包含TS0、TS16或越界值')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for reserved_slot in RESERVED:
        output[reserved_slot] = frame[reserved_slot]
    for output_slot, input_slot in mappings:
        output[output_slot] = frame[input_slot]
    return output
