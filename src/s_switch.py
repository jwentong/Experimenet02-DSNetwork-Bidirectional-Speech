"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

IDLE = 0xD5

def s_switch(input_frames, spatial_map):
    """
    input_frames: shape(2,32) np.uint8，2路输入链路帧
    spatial_map: dict key=(output_link, ts) → value=input_link
    返回 shape(2,32) np.uint8 2路输出链路帧
    S交换：时隙号不变，只切换输入链路；TS0/TS16本链路透传。
    映射出现非法链路、非法时隙、TS0/TS16，抛ValueError
    不修改 input_frames
    """
    out_frames = np.zeros((2, 32), dtype=np.uint8)
    num_link = 2

    # 校验spatial_map所有条目
    for (out_link, ts), in_link in spatial_map.items():
        # 链路必须0/1
        if out_link not in (0,1) or in_link not in (0,1):
            raise ValueError()
        # 时隙范围 0~31
        if not (0 <= ts <=31):
            raise ValueError()
        # S不允许映射TS0 TS16
        if ts ==0 or ts ==16:
            raise ValueError()

    # 遍历输出链路、时隙
    for out_link in range(num_link):
        for ts in range(32):
            if ts == 0 or ts ==16:
                # TS0 TS16：本链路原位透传
                out_frames[out_link, ts] = input_frames[out_link, ts]
            else:
                key = (out_link, ts)
                if key in spatial_map:
                    src_link = spatial_map[key]
                    out_frames[out_link, ts] = input_frames[src_link, ts]
                else:
                    out_frames[out_link, ts] = IDLE
    return out_frames

