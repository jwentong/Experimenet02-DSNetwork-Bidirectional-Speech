"""任务一：同一链路的时间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def _check_slot(slot):
    """业务时隙只能是TS1至TS31中排除TS16的位置。"""
    if not isinstance(slot, int) or isinstance(slot, bool):
        raise ValueError('时隙号必须是整数')
    if slot not in range(SLOTS) or slot in RESERVED:
        raise ValueError('时隙必须在0至31之间且不能是保留的TS0/TS16')

def t_switch(input_frame, control_memory):
    """输入uint8[32]，控制表{输出时隙:输入时隙}，返回新的uint8[32]。

    未连接输出填IDLE；TS0与TS16从输入同位置透传。
    映射的输入、输出必须是合法业务时隙，否则抛ValueError。
    不得原地修改输入帧。基础模型采用整帧缓存，时延由engine标记。
    """
    frame = np.asarray(input_frame, dtype=np.uint8)
    if frame.shape != (SLOTS,):
        raise ValueError('输入帧必须是长度32的uint8数组')
    # 先整体校验控制表，任何非法表项都在写输出之前拒绝。
    for out_slot, in_slot in control_memory.items():
        _check_slot(out_slot)
        _check_slot(in_slot)
    output = np.full(SLOTS, IDLE, dtype=np.uint8)
    for slot in RESERVED:                      # TS0/TS16 在本链路原位透传
        output[slot] = frame[slot]
    for out_slot, in_slot in control_memory.items():
        output[out_slot] = frame[in_slot]      # 输出时隙←输入时隙，不改动输入
    return output
