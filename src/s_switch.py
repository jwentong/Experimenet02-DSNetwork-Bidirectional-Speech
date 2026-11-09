"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _valid_link(link):
    return isinstance(link, (int, np.integer)) and not isinstance(link, bool) and 0 <= int(link) < LINKS


def _valid_slot(slot):
    return (
        isinstance(slot, (int, np.integer))
        and not isinstance(slot, bool)
        and 0 <= int(slot) < SLOTS
        and int(slot) not in RESERVED
    )


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS) or frames.dtype != np.uint8:
        raise ValueError('input_frames must be a uint8 array with shape (2, 32)')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    output[:, 0] = frames[:, 0]
    output[:, 16] = frames[:, 16]

    for key, in_link in spatial_map.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError('spatial mapping key must be (output_link, timeslot)')
        out_link, slot = key
        if not _valid_link(out_link) or not _valid_slot(slot) or not _valid_link(in_link):
            raise ValueError('spatial mapping must use links 0/1 and business timeslots TS1-TS31')
        output[int(out_link), int(slot)] = frames[int(in_link), int(slot)]

    return output
