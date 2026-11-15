"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _valid_slot(value):
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < SLOTS and value not in RESERVED


def _valid_link(value):
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < LINKS


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS) or frames.dtype != np.uint8:
        raise ValueError('输入必须是uint8[2,32]的两条PCM链路')

    for key, src_link in spatial_map.items():
        if not (isinstance(key, tuple) and len(key) == 2):
            raise ValueError('S控制表的键必须是(输出链路,时隙)二元组')
        out_link, slot = key
        if not _valid_link(out_link):
            raise ValueError('输出链路必须是0或1')
        if not _valid_slot(slot):
            raise ValueError('S控制表只能映射TS1至TS31的业务时隙，不能映射TS0/TS16或越界值')
        if not _valid_link(src_link):
            raise ValueError('输入链路必须是0或1')

    out = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    # 保留时隙沿本链路原位透传
    for link in range(LINKS):
        out[link, 0] = frames[link, 0]
        out[link, 16] = frames[link, 16]
    # S只换链路，不改时隙号
    for (out_link, slot), src_link in spatial_map.items():
        out[out_link, slot] = frames[src_link, slot]
    return out
