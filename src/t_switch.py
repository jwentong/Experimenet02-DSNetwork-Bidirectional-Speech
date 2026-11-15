"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS


def _valid_slot(value):
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < SLOTS and value not in RESERVED


def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame)
    if frame.shape != (SLOTS,) or frame.dtype != np.uint8:
        raise ValueError('输入必须是uint8[32]的PCM帧')

    # 先把整帧映射检查完，任何非法表项都不影响输入和输出
    for out_slot, in_slot in control_memory.items():
        if not _valid_slot(out_slot):
            raise ValueError('控制表的输出时隙必须是TS1至TS31的业务时隙，不能用TS0/TS16或越界值')
        if not _valid_slot(in_slot):
            raise ValueError('控制表的输入时隙必须是TS1至TS31的业务时隙，不能用TS0/TS16或越界值')

    out = np.full(SLOTS, IDLE, dtype=np.uint8)
    # 保留时隙原位透传
    out[0] = frame[0]
    out[16] = frame[16]
    # 按“输出指向输入”查表
    for out_slot, in_slot in control_memory.items():
        out[out_slot] = frame[in_slot]
    return out
