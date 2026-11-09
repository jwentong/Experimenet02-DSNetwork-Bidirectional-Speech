import numpy as np
from collections import deque

IDLE = 0xD5

def serve_packet(input_frame, queue, capacity):
    """
    包交换处理函数
    input_frame: np.ndarray, shape=(32,), uint8，一帧输入时隙
    queue: deque，存放待转发数据包（Pending对象）
    capacity: int，队列最大容量
    返回输出帧 out_frame
    规则:
    1. 输出帧默认全部填充IDLE
    2. 队列不空，取出队首包，如果包还有剩余字节，往输出时隙填数据
    3. 输入帧里找到数据包起始，生成Pending包对象，队列没满就入队
    4. 队列满则丢包
    5. 不修改input_frame
    """
    out_frame = np.full_like(input_frame, IDLE)

    # 先发送：队首包拿一个字节放到输出时隙0
    if len(queue) > 0:
        pkt = queue[0]
        out_frame[0] = pkt.pop_byte()
        if pkt.remaining <= 0:
            queue.popleft()

    # 扫描输入帧，寻找包起始标记0xAA
    for ts in range(32):
        b = input_frame[ts]
        if b == 0xAA:
            from src.models import Pending
            # 从当前时隙ts开始，取后面的字节作为包载荷
            payload = input_frame[ts:].copy()
            new_pkt = Pending(payload)
            if len(queue) < capacity:
                queue.append(new_pkt)
            # 队列满直接丢弃，什么都不做
    return out_frame


def serve_circuit(input_frame, tables):
    """
    电路交换服务函数，同帧式接口
    input_frame: np.ndarray(32,) uint8
    tables: 交换表（T/S表）
    返回 out_frame
    规则：查表转发，没有匹配通路就填IDLE
    """
    from src.connections import lookup
    out_frame = np.full_like(input_frame, IDLE)
    for ts in range(32):
        byte_val = input_frame[ts]
        if byte_val == IDLE:
            continue
        # 按当前时隙构造端点查表
        res = lookup(ts, tables)
        if res is not None:
            out_ts = res
            out_frame[out_ts] = byte_val
    return out_frame
