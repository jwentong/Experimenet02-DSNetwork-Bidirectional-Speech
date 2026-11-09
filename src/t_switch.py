"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def _validate_business_slot(slot, name):
    if not isinstance(slot, int) or slot not in range(SLOTS) or slot in RESERVED:
        raise ValueError(f"{name}必须使用TS1至TS31中的业务时隙，不能使用TS0或TS16")

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame=np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError("input_frame必须是长度32的uint8数组")

    output=np.full(SLOTS,IDLE,dtype=np.uint8)
    for slot in RESERVED:
        output[slot]=frame[slot]

    for output_slot,input_slot in control_memory.items():
        _validate_business_slot(output_slot,"输出时隙")
        _validate_business_slot(input_slot,"输入时隙")
        output[output_slot]=frame[input_slot]
    return output
