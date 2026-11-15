"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    # 创建新数组，全部默认填 IDLE
    out_frame = np.full(SLOTS, IDLE, dtype=np.uint8)
    
    # 透传 TS0 和 TS16
    out_frame[0] = input_frame[0]
    out_frame[16] = input_frame[16]
    
    for out_slot, in_slot in control_memory.items():
        # 校验：不能是保留时隙(0, 16)，且必须在 0~31 范围内
        if out_slot in (0, 16) or in_slot in (0, 16) or \
           not (0 <= out_slot < SLOTS) or not (0 <= in_slot < SLOTS):
            raise ValueError("Invalid or reserved time slot in control memory")
            
        out_frame[out_slot] = input_frame[in_slot]
        
    return out_frame
