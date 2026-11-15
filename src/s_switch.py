"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    output_frames = np.full_like(input_frames, IDLE, dtype=np.uint8)

    for link in range(LINKS):
        output_frames[link, 0] = input_frames[link, 0]
        output_frames[link, 16] = input_frames[link, 16]

    for (out_link, ts), in_link in spatial_map.items():
        if not (0 <= out_link < LINKS and 0 <= in_link < LINKS and 0 <= ts < SLOTS):
            raise ValueError(f"非法链路/时隙: out_link={out_link}, ts={ts}, in_link={in_link}")
        if ts in (0, 16):
            raise ValueError(f"TS0、TS16为保留时隙，不允许进入S交换映射")

        output_frames[out_link, ts] = input_frames[in_link, ts]

    return output_frames
