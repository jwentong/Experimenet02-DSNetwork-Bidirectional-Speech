"""任务二：同一时隙位置的空间交换。"""
import numpy as np
from src.models import IDLE, RESERVED, SLOTS, LINKS

def s_switch(input_frames, spatial_map):
    """输入uint8[2,32]，控制表{(输出链路,时隙):输入链路}。

    返回新的uint8[2,32]，S只改链路，不改时隙。
    未连接业务输出填IDLE；各输出链路TS0/16保留本链路输入。
    非法链路、时隙或保留时隙映射抛ValueError，不改输入。
    """
    frames = np.asarray(input_frames)
    if frames.shape != (LINKS, SLOTS) or frames.dtype != np.uint8:
        raise ValueError('input_frames must be a uint8 array with shape (2, 32)')

    output = np.full((LINKS, SLOTS), IDLE, dtype=np.uint8)
    output[:, list(RESERVED)] = frames[:, list(RESERVED)]

    for output_position, input_link in spatial_map.items():
        if (not isinstance(output_position, tuple) or len(output_position) != 2
                or not isinstance(output_position[0], (int, np.integer))
                or not isinstance(output_position[1], (int, np.integer))
                or not isinstance(input_link, (int, np.integer))):
            raise ValueError('S mappings must use (output_link, timeslot): input_link')

        output_link, timeslot = output_position
        if (output_link not in range(LINKS)
                or input_link not in range(LINKS)
                or timeslot not in range(SLOTS)
                or timeslot in RESERVED):
            raise ValueError('S mappings must use valid links and business timeslots')
        output[output_link, timeslot] = frames[input_link, timeslot]

    return output
