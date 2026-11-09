"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

"""输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。
未连接输出填IDLE；TS0与TS16从输入同位置透传。
映射的输入、输出必须是合法业务时隙，否则抛ValueError。
不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
"""

def t_switch(input_frame, control_memory):
    # 先创建输出帧，初始全部填充IDLE，注意拷贝，不改动input_frame
    output_frame = np.full_like(input_frame, IDLE)

    # TS0、TS16 保留时隙，直接透传
    output_frame[0] = input_frame[0]
    output_frame[16] = input_frame[16]

    # 遍历控制表：key=输出时隙，value=输入时隙
    for out_slot, in_slot in control_memory.items():
        # 校验：输出时隙、输入时隙都不能是保留时隙(0,16)，且在0~31范围内
        if out_slot in RESERVED or in_slot in RESERVED:
            raise ValueError("保留时隙TS0/TS16不允许配置交换映射")
        if not (0 <= out_slot < SLOTS and 0 <= in_slot < SLOTS):
            raise ValueError("时隙编号超出合法范围")

        # 执行时隙交换：输出时隙out_slot，取输入帧in_slot的数据
        output_frame[out_slot] = input_frame[in_slot]

    return output_frame
