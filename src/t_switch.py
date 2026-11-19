import numpy as np
from src.models import IDLE

def t_switch(link_frame, t_map):
    """
    时间交换 T-switch
    link_frame: 一维数组 shape(32,)，一条链路的一帧32个时隙
    t_map: dict {输出时隙: 输入时隙}
    返回新的一维帧 shape(32,)
    """
    out_frame = np.full(32, IDLE, dtype=np.uint8)
    for out_ts, in_ts in t_map.items():
        out_frame[out_ts] = link_frame[in_ts]
    return out_frame

