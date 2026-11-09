"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    out = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for ts in RESERVED:
            out[link, ts] = input_frames[link, ts]
    for (out_link, out_ts), in_link in spatial_map.items():
        if out_link < 0 or out_link >= LINKS:
            raise ValueError(f'非法输出链路 {out_link}')
        if out_ts in RESERVED or out_ts < 0 or out_ts >= SLOTS:
            raise ValueError(f'非法输出时隙 {out_ts}')
        if in_link < 0 or in_link >= LINKS:
            raise ValueError(f'非法输入链路 {in_link}')
        out[out_link, out_ts] = input_frames[in_link, out_ts]
    return out
