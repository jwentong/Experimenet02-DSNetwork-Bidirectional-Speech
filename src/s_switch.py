"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS


def _check_link(link, role):
    if isinstance(link, bool) or not isinstance(link, (int, np.integer)) or int(link) not in range(LINKS):
        raise ValueError(f'{role}链路必须是0或1')


def _check_slot(slot, role):
    if isinstance(slot, bool) or not isinstance(slot, (int, np.integer)):
        raise ValueError(f'{role}时隙必须是整数')
    if not 0 <= int(slot) < SLOTS or int(slot) in RESERVED:
        raise ValueError(f'{role}时隙必须是TS1至TS31中的业务时隙，不能使用TS0或TS16')


def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS):
        raise ValueError('输入帧必须是2条链路各32个时隙的数组')

    # 先整体校验；键必须是(输出链路,时隙)，值是输入链路。
    for key, input_link in spatial_map.items():
        try:
            output_link, output_ts = key
        except (TypeError, ValueError) as exc:
            raise ValueError('控制表键必须是(输出链路,时隙)') from exc
        _check_link(output_link, '输出')
        _check_slot(output_ts, '输出')
        _check_link(input_link, '输入')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    for link in range(LINKS):
        for slot in RESERVED:
            output[link, slot] = frames[link, slot]
    for (output_link, output_ts), input_link in spatial_map.items():
        output[output_link, output_ts] = frames[input_link, output_ts]
    return output
