"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    out = np.full(SLOTS, IDLE, dtype=np.uint8)
    for ts in RESERVED:
        out[ts] = input_frame[ts]
    for out_ts, in_ts in control_memory.items():
        if out_ts in RESERVED or out_ts < 0 or out_ts >= SLOTS:
            raise ValueError(f'非法输出时隙 {out_ts}')
        if in_ts in RESERVED or in_ts < 0 or in_ts >= SLOTS:
            raise ValueError(f'非法输入时隙 {in_ts}')
        out[out_ts] = input_frame[in_ts]
    return out
