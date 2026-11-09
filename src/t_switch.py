"""任务一：同一链路的时间交换。"""
import numpy as np

IDLE = 0xD5
NUM_SLOTS = 32
RESERVED = {0, 16}


def _check_ts(ts):
    if not isinstance(ts, int) or ts < 0 or ts >= NUM_SLOTS or ts in RESERVED:
        raise ValueError(f"illegal timeslot: {ts!r}")


def t_switch(input_frame, control_memory):
    # 1) 先校验，任何非法项直接抛，且此时还没碰输出
    for out_ts, in_ts in control_memory.items():
        _check_ts(out_ts)
        _check_ts(in_ts)

    # 2) 输出先全填 IDLE
    out = np.full(NUM_SLOTS, IDLE, dtype=np.uint8)

    # 3) TS0/16 原位透传（优先级最高）
    for ts in RESERVED:
        out[ts] = input_frame[ts]

    # 4) 业务时隙按控制表重排
    for out_ts, in_ts in control_memory.items():
        out[out_ts] = input_frame[in_ts]

    return out