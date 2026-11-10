"""任务二：S接线器，链路交换，时隙不变"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS

def s_switch(link_frames, s_map):
    """
    link_frames: np.ndarray, shape=(n_link, SLOTS) uint8，二维数组：[链路号，时隙]
    s_map: dict[(out_link, ts), in_link]
    返回 output_frames: np.ndarray, shape=(n_link, SLOTS) uint8
    TS0、TS16透传；不在s_map里的输出填IDLE；非法时隙抛ValueError
    """
    n_link = link_frames.shape[0]
    output = np.full_like(link_frames, fill_value=IDLE)

    forbidden_ts = {0, 16}
    seen_keys = set()
    # 前置校验所有映射
    for (ol, ts), il in s_map.items():
        # 校验输出链路ol
        if ol < 0 or ol >= n_link:
            raise ValueError(f"S接线器非法输出链路 {ol}")
        # 校验时隙
        if ts in forbidden_ts:
            raise ValueError(f"S接线器非法时隙 ts={ts}")
        if not (0 <= ts < SLOTS):
            raise ValueError(f"S接线器非法时隙 ts={ts}")
        # 校验输入链路il
        if il < 0 or il >= n_link:
            raise ValueError(f"S接线器非法输入链路 {il}")
        # 重复映射检查
        if (ol, ts) in seen_keys:
            raise ValueError(f"S接线器重复映射 (out_link={ol}, ts={ts})")
        seen_keys.add((ol, ts))

    # TS0、TS16：本链路透传
    output[:, 0] = link_frames[:, 0]
    output[:, 16] = link_frames[:, 16]

    # 执行S交换：时隙ts不变，数据从输入链路il → 输出链路ol
    for (ol, ts), il in s_map.items():
        output[ol, ts] = link_frames[il, ts]

    return output
