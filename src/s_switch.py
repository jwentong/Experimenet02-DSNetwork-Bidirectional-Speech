import numpy as np
from src.models import IDLE

def s_switch(frames, s_map):
    """
    s_map: {(out_link, out_ts): in_link}
    输出位置(out_link,out_ts)的数据，来自 in_link 这条链路、同一个时隙 out_ts
    frames: list[np.ndarray(32,)]，每条链路的帧
    返回 out: [link, timeslot] 二维数组
    """
    n_link = len(frames)
    out = np.full((n_link, 32), IDLE, dtype=np.uint8)

    for (out_link, out_ts), in_link in s_map.items():
        out[out_link, out_ts] = frames[in_link][out_ts]
    return out
