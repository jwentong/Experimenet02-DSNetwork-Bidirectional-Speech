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
        if out_ts not in range(SLOTS) or in_ts not in range(SLOTS):
            raise ValueError('控制表时隙必须为0至31的整数')
        if out_ts in RESERVED or in_ts in RESERVED:
            raise ValueError('TS0与TS16为保留时隙，不能写入控制表')
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError('输入帧必须包含32个uint8样本')
    out = np.full(SLOTS, IDLE, dtype=np.uint8)
    out[0] = frame[0]
    out[16] = frame[16]
    for out_ts, in_ts in control_memory.items():
        out[out_ts] = frame[in_ts]
    return out
