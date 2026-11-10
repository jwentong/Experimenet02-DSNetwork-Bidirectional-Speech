"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    # 拷贝输入帧，防止原地修改
    out_frame = np.copy(input_frame)

    # TS0、TS16 固定透传，不需要走控制表
    # 先全部填充IDLE，再覆盖保留时隙 + 控制表映射
    out_frame[:] = IDLE
    out_frame[0] = input_frame[0]
    out_frame[16] = input_frame[16]

    # 业务时隙范围：1~31，排除16
    valid_slots = set(range(1, 32)) - {16}

    for out_ts, in_ts in control_memory.items():
        # 校验：输入、输出时隙都必须是合法业务时隙
        if out_ts not in valid_slots or in_ts not in valid_slots:
            raise ValueError(f"非法业务时隙 out_ts={out_ts}, in_ts={in_ts}")
        # T接线器：输出时隙out_ts = 输入帧in_ts位置的数据
        out_frame[out_ts] = input_frame[in_ts]

    return out_frame

