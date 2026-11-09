"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _check_slot(slot, role):
    """控制表中的输入、输出时隙必须是TS1至TS31中的业务时隙。"""
    if isinstance(slot, bool) or not isinstance(slot, (int, np.integer)):
        raise ValueError(f'{role}时隙必须是整数')
    if not 0 <= int(slot) < SLOTS or int(slot) in RESERVED:
        raise ValueError(f'{role}时隙必须是TS1至TS31中的业务时隙，不能使用TS0或TS16')


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError('输入帧必须是长度32的一维数组')

    # 先整体校验，避免映射非法时产生半成品结果。
    for output_ts, input_ts in control_memory.items():
        _check_slot(output_ts, '输出')
        _check_slot(input_ts, '输入')

    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        output[slot] = frame[slot]
    for output_ts, input_ts in control_memory.items():
        output[output_ts] = frame[input_ts]
    return output
