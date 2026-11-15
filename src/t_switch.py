"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    output_frame = np.full_like(input_frame, IDLE, dtype=np.uint8)
    output_frame[0] = input_frame[0]
    output_frame[16] = input_frame[16]

    for out_ts, in_ts in control_memory.items():
        if not (0 <= out_ts < SLOTS and 0 <= in_ts < SLOTS):
            raise ValueError(f"时隙越界: out_ts={out_ts}, in_ts={in_ts}")
        if out_ts in (0, 16) or in_ts in (0, 16):
            raise ValueError(f"TS0、TS16是保留透传时隙，不允许配置进交换表")

        if input_frame[in_ts] == RESERVED:
            continue

        output_frame[out_ts] = input_frame[in_ts]

    return output_frame
