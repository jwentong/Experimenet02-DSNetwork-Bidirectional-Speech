
"""任务一：同一链路的时间交换。"""

import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """

    # 1. 检查控制表中的输入、输出时隙是否合法
    for output_ts, input_ts in control_memory.items():
        if (output_ts not in range(SLOTS) or
                input_ts not in range(SLOTS) or
                output_ts in RESERVED or
                input_ts in RESERVED):
            raise ValueError("控制表包含非法时隙或保留时隙")

    # 2. 创建新的输出帧，所有位置初始化为空闲值
    output_frame = np.full(SLOTS, IDLE, dtype=np.uint8)

    # 3. 保留时隙原位透传
    for ts in RESERVED:
        output_frame[ts] = input_frame[ts]

    # 4. 根据控制表进行时间交换
    for output_ts, input_ts in control_memory.items():
        output_frame[output_ts] = input_frame[input_ts]

    # 5. 返回新的输出帧
    return output_frame
