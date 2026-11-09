"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    num_slots = SLOTS if isinstance(SLOTS, int) else len(SLOTS)
    frame = np.asarray(input_frame, dtype=np.uint8)
    if frame.shape != (num_slots,):
        raise ValueError("input_frame 长度必须为 32")
    if not isinstance(control_memory, dict):
        raise ValueError("control_memory 必须为字典")

    for out_ts, in_ts in control_memory.items():
        if (
            isinstance(out_ts, bool)
            or isinstance(in_ts, bool)
            or not isinstance(out_ts, (int, np.integer))
            or not isinstance(in_ts, (int, np.integer))
        ):
            raise ValueError("时隙编号必须为整数")
        if not (0 <= out_ts < num_slots) or not (0 <= in_ts < num_slots):
            raise ValueError(f"时隙超出范围: {out_ts} <- {in_ts}")
        if out_ts in RESERVED or in_ts in RESERVED:
            raise ValueError(f"保留时隙不能配置业务映射: {out_ts} <- {in_ts}")

    output_frame = np.full(num_slots, IDLE, dtype=np.uint8)
    for r_ts in RESERVED:
        output_frame[r_ts] = frame[r_ts]

    for out_ts, in_ts in control_memory.items():
        output_frame[int(out_ts)] = frame[int(in_ts)]

    return output_frame


