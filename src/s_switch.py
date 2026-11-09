import numpy as np
from src.models import IDLE, SLOTS, LINKS, RESERVED

def s_switch(input_frames, spatial_map):
    """
    input_frames: 2 x 32 的输入帧
    spatial_map: s_map，字典 {(out_link, out_ts): in_link}
    """
    # 生成 2 x 32 的全 IDLE 的 uint8 数组
    out = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    
    # 每条链路的 TS0/16 原位透传
    for link in range(LINKS):
        for ts in RESERVED:
            out[link, ts] = input_frames[link, ts]
            
    # 遍历映射表
    for (out_link, out_ts), in_link in spatial_map.items():
        if out_link not in range(LINKS) or in_link not in range(LINKS):
            raise ValueError("Invalid link")
        if out_ts in RESERVED:
            raise ValueError("Cannot map reserved timeslot")
        if not (0 <= out_ts < SLOTS):
            raise ValueError("Timeslot out of range")
            
        # S 交换只改变链路，不改变时隙
        out[out_link, out_ts] = input_frames[in_link, out_ts]
        
    return out