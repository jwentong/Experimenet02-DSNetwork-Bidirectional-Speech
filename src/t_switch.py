"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    # 1. 检查控制表是否合法（不能包含保留时隙、不能越界）
    for out_ts, in_ts in control_memory.items():
        if out_ts in RESERVED or in_ts in RESERVED:
            raise ValueError("控制表不能映射保留时隙(TS0/TS16)")
        if not (1 <= out_ts < SLOTS) or not (1 <= in_ts < SLOTS):
            raise ValueError("控制表时隙超出业务范围")

    # 2. 创建新的输出帧，全部默认填充为 IDLE (0xD5)
    # 使用 np.full 保证类型是 uint8，长度是 SLOTS (32)
    out_frame = np.full(SLOTS, IDLE, dtype=np.uint8)

    # 3. 处理 TS0 和 TS16，从输入原位透传
    for ts in RESERVED:
        out_frame[ts] = input_frame[ts]

    # 4. 根据控制表，将输入时隙的数据搬到对应的输出时隙
    for out_ts, in_ts in control_memory.items():
        out_frame[out_ts] = input_frame[in_ts]

    # 5. 返回新数组（没有修改原输入）
    return out_frame