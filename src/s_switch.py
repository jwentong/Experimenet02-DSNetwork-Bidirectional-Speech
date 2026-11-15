"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    out_frames = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    
    # 透传 TS0 和 TS16
    for link in range(LINKS):
        out_frames[link, 0] = input_frames[link, 0]
        out_frames[link, 16] = input_frames[link, 16]
        
    for (out_link, ts), in_link in spatial_map.items():
        # 校验链路号
        if not (0 <= out_link < LINKS) or not (0 <= in_link < LINKS):
            raise ValueError("Invalid link ID")
        # 校验时隙号：不能是保留时隙，且必须在范围内
        if ts in (0, 16) or not (0 <= ts < SLOTS):
            raise ValueError("Invalid or reserved time slot")
            
        out_frames[out_link, ts] = input_frames[in_link, ts]
        
    return out_frames