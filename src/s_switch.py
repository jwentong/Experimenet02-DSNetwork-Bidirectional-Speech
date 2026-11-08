"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    if (not isinstance(input_frames, np.ndarray)
            or input_frames.shape != (LINKS, SLOTS)
            or input_frames.dtype != np.uint8):
        raise ValueError('S输入必须是uint8[2,32]数组')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[:, slot] = input_frames[:, slot]

    for destination, in_link in spatial_map.items():
        if not isinstance(destination, tuple) or len(destination) != 2:
            raise ValueError('S输出位置必须是(链路,时隙)')
        out_link, slot = destination
        for link in (out_link, in_link):
            if (not isinstance(link, (int, np.integer))
                    or isinstance(link, (bool, np.bool_))
                    or link not in range(LINKS)):
                raise ValueError('S映射链路必须为0或1')
        if (not isinstance(slot, (int, np.integer))
                or isinstance(slot, (bool, np.bool_))
                or slot not in range(SLOTS) or slot in RESERVED):
            raise ValueError('S映射必须使用合法业务时隙')
        output[out_link, slot] = input_frames[in_link, slot]
    return output
