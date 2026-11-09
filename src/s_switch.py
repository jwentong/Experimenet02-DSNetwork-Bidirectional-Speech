"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('S输入必须是形状为(2,32)的uint8数组')
    for (out_link, ts), in_link in spatial_map.items():
        if out_link not in range(LINKS) or in_link not in range(LINKS):
            raise ValueError('S控制表的输入、输出链路必须是0或1')
        if ts not in range(SLOTS) or ts in RESERVED:
            raise ValueError('S控制表只能使用TS1至TS31中的业务时隙，不能使用TS0或TS16')
    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for ts in RESERVED:
            output[link, ts] = frames[link, ts]
    for (out_link, ts), in_link in spatial_map.items():
        output[out_link, ts] = frames[in_link, ts]
    return output
