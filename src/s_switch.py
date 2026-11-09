"""任务二：同一时隙位置的空间交换。"""
from numbers import Integral

import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _is_business_position(link_id, timeslot):
    return (
        isinstance(link_id, Integral)
        and not isinstance(link_id, bool)
        and 0 <= link_id < LINKS
        and isinstance(timeslot, Integral)
        and not isinstance(timeslot, bool)
        and 0 <= timeslot < SLOTS
        and timeslot not in RESERVED
    )

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError(f'输入帧必须是{LINKS}x{SLOTS}的二维数组')
    frames = np.asarray(frames, dtype=np.uint8)

    try:
        mappings = list(spatial_map.items())
    except (AttributeError, TypeError) as exc:
        raise ValueError('S控制表必须由(输出链路,时隙)映射到输入链路') from exc

    # 先校验全部表项，再生成输出，避免非法表项造成部分交换。
    for output_position, input_link in mappings:
        if not isinstance(output_position, tuple) or len(output_position) != 2:
            raise ValueError('S控制表的键必须是(输出链路,时隙)')
        output_link, timeslot = output_position
        if not _is_business_position(output_link, timeslot):
            raise ValueError('S控制表不能映射保留或非法链路/时隙')
        if (
            not isinstance(input_link, Integral)
            or isinstance(input_link, bool)
            or not 0 <= input_link < LINKS
        ):
            raise ValueError('S控制表的输入链路必须是0或1')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for reserved_slot in RESERVED:
        output[:, reserved_slot] = frames[:, reserved_slot]
    for (output_link, timeslot), input_link in mappings:
        output[output_link, timeslot] = frames[input_link, timeslot]
    return output
