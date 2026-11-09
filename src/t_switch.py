"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    for out_ts, in_ts in control_memory.items():
        if out_ts not in range(SLOTS) or out_ts in RESERVED or in_ts not in range(SLOTS) or in_ts in RESERVED:
            raise ValueError('控制表必须使用TS1至TS31中的业务时隙，不能使用保留时隙')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[slot] = input_frame[slot]
    for out_ts, in_ts in control_memory.items():
        output[out_ts] = input_frame[in_ts]
    return output
