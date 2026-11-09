"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙: 输入时隙}，返回新的uint8[32]。
    
    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    # 1. 创建输出帧，默认全填 IDLE
    output_frame = np.full(32, IDLE, dtype=np.uint8)

    # 2. 保留位置（TS0 和 TS16）原位透传
    for ts in RESERVED:
        output_frame[ts] = input_frame[ts]

    # 3. 遍历控制表，检查合法性并完成 T 交换
    for out_ts, in_ts in control_memory.items():
        # 检查是否超范围
        if out_ts < 0 or out_ts >= SLOTS or in_ts < 0 or in_ts >= SLOTS:
            raise ValueError(f"时隙超范围: out={out_ts}, in={in_ts}")
        
        # 检查是否映射到了保留时隙
        if out_ts in RESERVED or in_ts in RESERVED:
            raise ValueError(f"不能映射到保留时隙: out={out_ts}, in={in_ts}")

        # 执行时间交换
        output_frame[out_ts] = input_frame[in_ts]

    return output_frame
