"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from numbers import Integral
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    if not isinstance(input_frames, np.ndarray) or input_frames.shape != (LINKS, SLOTS) or input_frames.dtype != np.uint8:
        raise ValueError('输入帧必须为uint8[2,32]数组')
    for key, input_link in spatial_map.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError('空间控制表的键必须为(输出链路,时隙)')
        output_link, slot = key
        for value, limit in ((output_link, LINKS), (input_link, LINKS), (slot, SLOTS)):
            if not isinstance(value, Integral) or isinstance(value, bool) or not 0 <= value < limit:
                raise ValueError('非法链路或时隙')
        if slot in RESERVED:
            raise ValueError('保留时隙不能映射')
    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[:, slot] = input_frames[:, slot]
    for (output_link, slot), input_link in spatial_map.items():
        output[output_link, slot] = input_frames[input_link, slot]
    return output
