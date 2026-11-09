"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def _check_link(link):
    if not isinstance(link, int) or isinstance(link, bool):
        raise ValueError('链路号必须是整数')
    if link not in range(LINKS):
        raise ValueError('链路号只能是0或1')

def _check_slot(slot):
    if not isinstance(slot, int) or isinstance(slot, bool):
        raise ValueError('时隙号必须是整数')
    if slot not in range(SLOTS) or slot in RESERVED:
        raise ValueError('时隙必须在0至31之间且不能是保留的TS0/TS16')

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames, dtype=np.uint8)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('输入必须是2条链路各32时隙的uint8数组')
    for key, src_link in spatial_map.items():
        out_link, slot = key
        _check_link(out_link)
        _check_slot(slot)
        _check_link(src_link)
    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):                  # 保留时隙沿本链路原位透传
        for slot in RESERVED:
            output[link, slot] = frames[link, slot]
    for (out_link, slot), src_link in spatial_map.items():
        output[out_link, slot] = frames[src_link, slot]   # 只换链路，时隙不变
    return output
