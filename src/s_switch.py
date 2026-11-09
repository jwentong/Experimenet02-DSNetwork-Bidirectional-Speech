"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _check_link(value, role):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f'{role}链路必须是整数：{value!r}')
    if value not in range(LINKS):
        raise ValueError(f'{role}链路{value}非法：只允许链路0与1')


def _check_slot(value):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f'时隙必须是整数：{value!r}')
    if value not in range(SLOTS) or value in RESERVED:
        raise ValueError(f'时隙{value}非法：S单元不能映射TS0与TS16，且不得超过TS31')


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError(f'输入必须是{LINKS}x{SLOTS}的二维数组，当前为{frames.shape}')
    mappings = []
    for key, src_link in spatial_map.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError(f'控制表键必须是(输出链路,时隙)二元组：{key!r}')
        out_link, timeslot = key
        _check_link(out_link, '输出')
        _check_slot(timeslot)
        _check_link(src_link, '输入')
        mappings.append((int(out_link), int(timeslot), int(src_link)))
    result = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for slot in RESERVED:
            result[link, slot] = frames[link, slot]
    # 时隙号沿用输出位置，只把字节来源换成被选中的输入链路。
    for out_link, timeslot, src_link in mappings:
        result[out_link, timeslot] = frames[src_link, timeslot]
    return result
