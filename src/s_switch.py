"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    for (out_link, ts), in_link in spatial_map.items():
        if out_link not in range(LINKS) or in_link not in range(LINKS):
            raise ValueError('链路号只能为0或1')
        if ts not in range(SLOTS):
            raise ValueError('时隙必须为0至31的整数')
        if ts in RESERVED:
            raise ValueError('TS0与TS16为保留时隙，不能写入控制表')
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('输入帧必须为2条链路、每链路32个uint8样本')
    out = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        out[link, 0] = frames[link, 0]
        out[link, 16] = frames[link, 16]
    for (out_link, ts), in_link in spatial_map.items():
        out[out_link, ts] = frames[in_link, ts]
    return out
