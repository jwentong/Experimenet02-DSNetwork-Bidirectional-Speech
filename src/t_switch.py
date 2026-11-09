import numpy as np
from src.models import IDLE, SLOTS, RESERVED

def t_switch(input_frame, control_memory):
    """
    input_frame: 长度 32 的输入帧 (np.uint8)
    control_memory: t_maps[input_link]，字典格式 {output_ts: input_ts}
    """
    # 使用 numpy 生成一个全为 IDLE 的 uint8 数组
    out = np.full(SLOTS, IDLE, dtype=np.uint8)
    
    # TS0 和 TS16 原位透传
    for ts in RESERVED:
        out[ts] = input_frame[ts]
        
    # 遍历控制表字典
    for out_ts, in_ts in control_memory.items():
        # 校验非法情况
        if out_ts in RESERVED or in_ts in RESERVED:
            raise ValueError("Cannot map reserved timeslots")
        if not (0 <= out_ts < SLOTS) or not (0 <= in_ts < SLOTS):
            raise ValueError("Timeslot out of range")
            
        out[out_ts] = input_frame[in_ts]
        
    return out