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

    for output, input_link in spatial_map.items():
        if not isinstance(output, tuple) or len(output) != 2:
            raise ValueError("S 交换的输出位置必须由链路号和时隙号组成")
        output_link, slot = output
        if any(
            not isinstance(link, Integral)
            or isinstance(link, bool)
            or not 0 <= link < LINKS
            for link in (output_link, input_link)
        ):
            raise ValueError("S 交换的输入链路或输出链路无效")
        if (
            not isinstance(slot, Integral)
            or isinstance(slot, bool)
            or not 0 <= slot < SLOTS
            or slot in RESERVED
        ):
            raise ValueError("S 交换只能映射合法业务时隙")
        output_frames[output_link, slot] = input_frames[input_link, slot]
    return output_frames
