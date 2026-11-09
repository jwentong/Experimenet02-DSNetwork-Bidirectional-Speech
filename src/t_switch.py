"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

IDLE = 0xD5

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    # 不修改原输入，复制副本
    out_frame = np.zeros(32, dtype=np.uint8)

    # --------校验控制表每一项：输出时隙key，输入时隙val--------
    for out_ts, in_ts in control_memory.items():
        # 判断输出时隙合法性：必须1~31，不能0、16，不能越界负数
        if not (1 <= out_ts <=31) or out_ts ==16:
            raise ValueError()
        # 判断输入时隙合法性
        if not (1 <= in_ts <=31) or in_ts ==16:
            raise ValueError()

    # 逐时隙填充输出帧
    for slot in range(32):
        if slot == 0 or slot ==16:
            # TS0 TS16原位透传
            out_frame[slot] = input_frame[slot]
        else:
            if slot in control_memory:
                # 存在映射：输出时隙slot，取control_memory[slot]作为输入时隙
                src_ts = control_memory[slot]
                out_frame[slot] = input_frame[src_ts]
            else:
                # 无映射，填空闲
                out_frame[slot] = IDLE
    return out_frame
