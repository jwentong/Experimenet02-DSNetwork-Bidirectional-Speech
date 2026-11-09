"""任务二：同一时隙位置的空间交换。"""
import numbers

import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _business_slot(value):
    if not isinstance(value, numbers.Integral):
        raise ValueError('时隙必须为整数')
    value = int(value)
    if value not in range(SLOTS) or value in RESERVED:
        raise ValueError('映射必须使用0~31范围内的业务时隙（不含TS0/TS16）')
    return value


def _link(value):
    if not isinstance(value, numbers.Integral) or int(value) not in range(LINKS):
        raise ValueError('链路号必须为0或1')
    return int(value)


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('输入帧组必须为形状[2,32]的数组')
    frames = frames.astype(np.uint8, copy=False)

    mappings = []
    for key, source_link in spatial_map.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError('空间映射键必须为(输出链路,时隙)')
        out_link = _link(key[0])
        slot = _business_slot(key[1])
        source_link = _link(source_link)
        mappings.append((out_link, slot, source_link))

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[:, slot] = frames[:, slot]
    for out_link, slot, source_link in mappings:
        output[out_link, slot] = frames[source_link, slot]
    return output
