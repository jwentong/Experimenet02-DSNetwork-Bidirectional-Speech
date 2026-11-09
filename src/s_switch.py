"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _validate_link(value, *, name):
    if not isinstance(value, (int, np.integer)) or isinstance(value, bool):
        raise ValueError(f'{name} 必须是合法的整数链路号')
    value = int(value)
    if value not in range(LINKS):
        raise ValueError(f'{name} 必须落在 0..{LINKS-1}')
    return value


def _validate_slot(value, *, name):
    if not isinstance(value, (int, np.integer)) or isinstance(value, bool):
        raise ValueError(f'{name} 必须是合法的整数时隙号')
    value = int(value)
    if value not in range(SLOTS) or value in RESERVED:
        raise ValueError(f'{name} 不能使用保留时隙或越界时隙')
    return value


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames, dtype=np.uint8)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('input_frames 必须是 shape=(2,32) 的 uint8 数组')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for slot in range(SLOTS):
            if slot in RESERVED:
                output[link, slot] = frames[link, slot]

    for (out_link, out_slot), in_link in spatial_map.items():
        out_link = _validate_link(out_link, name='输出链路')
        out_slot = _validate_slot(out_slot, name='输出时隙')
        in_link = _validate_link(in_link, name='输入链路')
        output[out_link, out_slot] = frames[in_link, out_slot]

    return output.astype(np.uint8, copy=False)
