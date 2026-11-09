"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def _validate_link(link, name):
    if not isinstance(link,int) or link not in range(LINKS):
        raise ValueError(f"{name}必须是链路0或1")

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames=np.asarray(input_frames)
    if frames.shape != (LINKS,SLOTS):
        raise ValueError("input_frames必须是形状为(2, 32)的uint8数组")

    output=np.full((LINKS,SLOTS),IDLE,dtype=np.uint8)
    for link in range(LINKS):
        for slot in RESERVED:
            output[link,slot]=frames[link,slot]

    for key,input_link in spatial_map.items():
        if not isinstance(key,tuple) or len(key)!=2:
            raise ValueError("S控制表键必须是(输出链路,时隙)")
        output_link,slot=key
        _validate_link(output_link,"输出链路")
        _validate_link(input_link,"输入链路")
        if not isinstance(slot,int) or slot not in range(SLOTS) or slot in RESERVED:
            raise ValueError("时隙必须使用TS1至TS31中的业务时隙，不能使用TS0或TS16")
        output[output_link,slot]=frames[input_link,slot]
    return output
