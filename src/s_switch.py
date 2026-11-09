"""任务二：同一时隙位置的空间交换。"""
import numpy as np

IDLE = 0xD5
NUM_LINKS = 2
NUM_SLOTS = 32
RESERVED = {0, 16}


def _check_link(link):
    if not isinstance(link, (int, np.integer)) or link < 0 or link >= NUM_LINKS:
        raise ValueError(f"illegal link: {link!r}")


def _check_ts(ts):
    if not isinstance(ts, (int, np.integer)) or ts < 0 or ts >= NUM_SLOTS or ts in RESERVED:
        raise ValueError(f"illegal timeslot: {ts!r}")


def s_switch(input_frames, spatial_map):
    # 1) 校验 map：(out_link, ts) -> in_link
    for (out_link, ts), in_link in spatial_map.items():
        _check_link(out_link)
        _check_ts(ts)
        _check_link(in_link)

    # 2) 输出 (2,32) 全填 IDLE
    out = np.full((NUM_LINKS, NUM_SLOTS), IDLE, dtype=np.uint8)

    # 3) 每条链路 TS0/16 沿本链路原位透传
    for link in range(NUM_LINKS):
        for ts in RESERVED:
            out[link, ts] = input_frames[link][ts]

    # 4) 其余按 map 换链路，时隙不变
    for (out_link, ts), in_link in spatial_map.items():
        out[out_link, ts] = input_frames[in_link][ts]

    return out
