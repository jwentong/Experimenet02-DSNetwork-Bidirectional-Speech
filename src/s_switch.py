"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    num_links = LINKS if isinstance(LINKS, int) else len(LINKS)
    num_slots = SLOTS if isinstance(SLOTS, int) else len(SLOTS)
    frames = np.asarray(input_frames, dtype=np.uint8)
    if frames.shape != (num_links, num_slots):
        raise ValueError("input_frames 形状必须为 (2, 32)")
    if not isinstance(spatial_map, dict):
        raise ValueError("spatial_map 必须为字典")

    for key, in_link in spatial_map.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError("spatial_map 键必须为 (output_link, timeslot)")
        out_link, ts = key
        if (
            isinstance(out_link, bool)
            or isinstance(ts, bool)
            or isinstance(in_link, bool)
            or not isinstance(out_link, (int, np.integer))
            or not isinstance(ts, (int, np.integer))
            or not isinstance(in_link, (int, np.integer))
        ):
            raise ValueError("链路号与时隙号必须为整数")
        if not (0 <= out_link < num_links) or not (0 <= in_link < num_links):
            raise ValueError(f"链路号超出范围: out={out_link}, in={in_link}")
        if not (0 <= ts < num_slots) or ts in RESERVED:
            raise ValueError(f"非法或保留时隙: {ts}")

    output_frames = np.full((num_links, num_slots), IDLE, dtype=np.uint8)
    for r_ts in RESERVED:
        output_frames[:, r_ts] = frames[:, r_ts]

    for (out_link, ts), in_link in spatial_map.items():
        output_frames[int(out_link), int(ts)] = frames[int(in_link), int(ts)]

    return output_frames


