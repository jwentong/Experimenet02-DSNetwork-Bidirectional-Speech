"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for (out_link, slot), in_link in spatial_map.items():
        if (out_link not in range(LINKS) or in_link not in range(LINKS)
                or slot not in range(SLOTS) or slot in RESERVED):
            raise ValueError('S交换映射只能使用链路0/1与TS1至TS31中的业务时隙')
        output[out_link, slot] = input_frames[in_link, slot]
    # 各输出链路的保留时隙沿本链路原位透传
    output[:, 0] = input_frames[:, 0]
    output[:, 16] = input_frames[:, 16]
    return output
