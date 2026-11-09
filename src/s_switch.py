"""任务二：同一时隙位置的空间交换。"""

"""输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。
返回新的uint8[2,32]，S只改链路，不改时隙。
未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
非法链路、时隙或保留时隙映射抛ValueError，不改输入。
"""

import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def s_switch(input_frames, spatial_map):
    """
    input_frames: list[np.ndarray], 2条输入链路，每条32时隙uint8帧
    spatial_map: dict[(out_link, ts)] = in_link
    返回 output_frames：[链路0帧, 链路1帧]，shape(2,32)
    """
    # 初始化两路输出帧，全部填IDLE
    out0 = np.full_like(input_frames[0], IDLE)
    out1 = np.full_like(input_frames[1], IDLE)
    output_frames = [out0, out1]

    # TS0 TS16：各链路原位透传
    for link in range(LINKS):
        output_frames[link][0] = input_frames[link][0]
        output_frames[link][16] = input_frames[link][16]

    # 遍历S控制表
    for (out_link, out_ts), in_link in spatial_map.items():
        # 参数合法性校验
        if out_ts in RESERVED:
            raise ValueError("TS0/TS16保留时隙不允许S交换映射")
        if not (0 <= out_link < LINKS and 0 <= in_link < LINKS):
            raise ValueError("链路编号越界")
        if not (0 <= out_ts < SLOTS):
            raise ValueError("时隙编号越界")

        # S交换：时隙不变，取对应输入链路相同时隙的数据
        output_frames[out_link][out_ts] = input_frames[in_link][out_ts]

    return np.array(output_frames)
