"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _check_slot(value, role):
    """业务时隙必须是0至31之间且不属于保留位置的整数。"""
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f'{role}时隙必须是整数：{value!r}')
    if value not in range(SLOTS) or value in RESERVED:
        raise ValueError(f'{role}时隙{value}非法：只允许TS1至TS31且不含TS16')


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,):
        raise ValueError(f'输入帧必须是长度{SLOTS}的一维数组，当前为{frame.shape}')
    # 先整体校验，任何一条映射非法都不产生输出，也不触碰输入帧。
    mappings = []
    for out_ts, in_ts in control_memory.items():
        _check_slot(out_ts, '输出')
        _check_slot(in_ts, '输入')
        mappings.append((int(out_ts), int(in_ts)))
    result = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:
        result[slot] = frame[slot]
    for out_ts, in_ts in mappings:
        result[out_ts] = frame[in_ts]
    return result
