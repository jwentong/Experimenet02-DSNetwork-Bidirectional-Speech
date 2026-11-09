"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    for (out_link, slot), in_link in spatial_map.items():
        if out_link not in range(LINKS) or in_link not in range(LINKS) or slot not in range(SLOTS) or slot in RESERVED:
            raise ValueError('空间映射必须使用链路0/1与TS1至TS31中的业务时隙')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for slot in RESERVED:
            output[link, slot] = input_frames[link, slot]
    for (out_link, slot), in_link in spatial_map.items():
        output[out_link, slot] = input_frames[in_link, slot]
    return output
