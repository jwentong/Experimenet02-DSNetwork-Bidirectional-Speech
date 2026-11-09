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
    if frame.shape != (SLOTS,):
        raise ValueError('T输入必须是长度32的uint8数组')
    for out_ts, in_ts in control_memory.items():
        for ts in (out_ts, in_ts):
            if ts not in range(SLOTS) or ts in RESERVED:
                raise ValueError('T控制表只能使用TS1至TS31中的业务时隙，不能使用TS0或TS16')
    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for ts in RESERVED:
        output[ts] = frame[ts]
    for out_ts, in_ts in control_memory.items():
        output[out_ts] = frame[in_ts]
    return output
