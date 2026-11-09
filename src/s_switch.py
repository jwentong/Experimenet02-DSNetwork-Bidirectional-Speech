"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路, 时隙): 输入链路}。

    返回新的uint8[2,32]。S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不修改输入。
    """
    # 1. 创建输出帧，默认全填 IDLE
    output_frames = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    
    # 2. 每条链路的保留时隙 (TS0 和 TS16) 原位透传
    for link in range(LINKS):
        for ts in RESERVED:
            output_frames[link][ts] = input_frames[link][ts]

    # 3. 遍历控制表，检查合法性并完成 S 交换
    for (out_link, ts), in_link in spatial_map.items():
        # 检查链路是否越界
        if out_link < 0 or out_link >= LINKS or in_link < 0 or in_link >= LINKS:
            raise ValueError(f"链路非法: out={out_link}, in={in_link}")
            
        # 检查时隙是否越界
        if ts < 0 or ts >= SLOTS:
            raise ValueError(f"时隙非法: {ts}")
            
        # 检查是否映射到了保留时隙
        if ts in RESERVED:
            raise ValueError(f"不能映射保留时隙: {ts}")
            
        # 执行空间交换：保持时隙不变，改变链路
        output_frames[out_link][ts] = input_frames[in_link][ts]

    return output_frames
