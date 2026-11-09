"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2, 32]，控制表{(输出链路, 时隙): 输入链路}，返回新的uint8[2, 32]。"""
    
    # 1. 检查控制表是否合法
    for (out_link, ts), in_link in spatial_map.items():
        # 检查时隙和链路是否越界
        if not (0 <= out_link < 2) or not (0 <= in_link < 2):
            raise ValueError("链路号超出范围")
        if not (0 <= ts < SLOTS):
            raise ValueError("时隙超出范围")
        # 不能映射保留时隙
        if ts in RESERVED:
            raise ValueError("不能映射保留时隙(TS0/TS16)")

    # 2. 创建新的输出帧，形状是 (2, 32)，全填 IDLE
    out_frames = np.full((2, SLOTS), IDLE, dtype=np.uint8)

    # 3. 遍历每一条输出链路和每一个时隙
    for out_link in range(2):
        for ts in range(SLOTS):
            if ts in RESERVED:
                # 保留时隙：沿本链路原位透传
                out_frames[out_link, ts] = input_frames[out_link, ts]
            elif (out_link, ts) in spatial_map:
                # 有映射：从指定的输入链路取相同位置的数据
                in_link = spatial_map[(out_link, ts)]
                out_frames[out_link, ts] = input_frames[in_link, ts]

    return out_frames