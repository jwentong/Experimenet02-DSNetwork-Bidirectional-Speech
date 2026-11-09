"""任务二：同一时隙位置的空间交换。"""
from numbers import Integral

import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    output_frames = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output_frames[:, slot] = input_frames[:, slot]

    for (output_link, slot), input_link in spatial_map.items():
        for link in (output_link, input_link):
            if not isinstance(link, Integral) or isinstance(link, bool) or link not in range(LINKS):
                raise ValueError(f'S交换需要合法的链路号：{link!r}')
        if not isinstance(slot, Integral) or isinstance(slot, bool):
            raise ValueError(f'时隙号必须是整数：{slot!r}')
        if slot not in range(SLOTS) or slot in RESERVED:
            raise ValueError(f'S交换需要合法的业务时隙：{slot}')
        output_frames[output_link, slot] = input_frames[input_link, slot]

    return output_frames
