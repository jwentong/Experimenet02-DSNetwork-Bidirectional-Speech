
"""任务二：同一时隙位置的空间交换。"""

import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """

    # 1. 检查空间交换控制表是否合法
    for (output_link, ts), input_link in spatial_map.items():
        if (output_link not in range(LINKS) or
                input_link not in range(LINKS) or
                ts not in range(SLOTS) or
                ts in RESERVED):
            raise ValueError("控制表包含非法链路或非法时隙")

    # 2. 创建新的输出帧，全部初始化为空闲值
    output_frames = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)

    # 3. 保留时隙原位透传
    for link in range(LINKS):
        for ts in RESERVED:
            output_frames[link, ts] = input_frames[link, ts]

    # 4. 按控制表进行空间交换
    for (output_link, ts), input_link in spatial_map.items():
        output_frames[output_link, ts] = input_frames[input_link, ts]

    # 5. 返回新的输出帧
    return output_frames
