"""自拟反例：三条连接并存、释放后内部T资源必须真正回收。

手算前提（输入帧 x 由 build_frame 构造，每个位置字节不同）：
1) C1 连接 A=(0,1) 与 B=(1,5)：A→B 为 T0[5]=1 与 S[(1,5)]=0；B→A 为 T1[1]=5 与 S[(0,1)]=1。
2) C3 连接 P=(0,4) 与 Q=(1,1)：P→Q 为 T0[1]=4 与 S[(1,1)]=0；Q→P 为 T1[4]=1 与 S[(0,4)]=1。
   注意 T1[1] 已被 C1 占用，但 C3 反向用的是 T1[4]，因此两条连接应当同时成立。
3) TS0、TS16 在任何单元都按本链路原位透传；未连接的业务时隙输出 IDLE=0xD5。
4) 释放 C1 后，T0[5] 应被回收，于是 (0,3) 与 (1,5) 可以重新建立；C3 在此期间继续传送。
"""
import numpy as np
from src.models import Endpoint, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import exchange_frame, run_frames


def build_frame(frame_id=0):
    """与教师 sample_frame 不同的字节模式，避免字节值与位置一一对应造成漏判。"""
    return np.array([[(63 * link + 29 * slot + 41 * frame_id + 7) % 256 for slot in range(32)] for link in range(2)], dtype=np.uint8)


def test_three_pairs_release_and_reuse():
    tables = Tables()
    a, b = Endpoint(0, 1), Endpoint(1, 5)
    p, q = Endpoint(0, 4), Endpoint(1, 1)
    assert connect_pair('C1', a, b, tables) is True
    assert connect_pair('C3', p, q, tables) is True

    frame = build_frame(0)
    out = exchange_frame(frame, tables)

    # 双向逐字节正确：C1 两个方向
    assert out[1, 5] == frame[0, 1]
    assert out[0, 1] == frame[1, 5]
    # 双向逐字节正确：C3 两个方向，且与 C1 的 T1[1] 不冲突
    assert out[1, 1] == frame[0, 4]
    assert out[0, 4] == frame[1, 1]
    # 保留时隙原位透传，未连接业务时隙填 IDLE
    assert np.array_equal(out[:, [0, 16]], frame[:, [0, 16]])
    assert out[0, 9] == IDLE and out[1, 30] == IDLE
    # 一帧延迟：第 2 帧的结果在第 3 帧可用，且取的是该帧自己的字节
    frames = [build_frame(k) for k in range(3)]
    records = run_frames(frames, tables)
    assert records[2]['available_frame_id'] == 3
    assert records[2]['output'][1, 5] == frames[2][0, 1]

    # 释放 C1 只清除它自己的四个表项，C3 的表项必须保留
    assert disconnect_pair('C1', tables) is True
    assert tables.s_map == {(1, 1): 0, (0, 4): 1}
    assert tables.t_maps == [{1: 4}, {4: 1}]
    survivor = exchange_frame(frame, tables)
    assert survivor[1, 1] == frame[0, 4] and survivor[0, 4] == frame[1, 1]
    assert survivor[1, 5] == IDLE and survivor[0, 1] == IDLE

    # 释放后 C1 占用的内部 T 输出 T0[5] 必须可被新连接使用
    assert connect_pair('C5', Endpoint(0, 3), Endpoint(1, 5), tables) is True
    assert tables.t_maps[0][5] == 3
    reused = exchange_frame(frame, tables)
    assert reused[1, 5] == frame[0, 3]
    # 重复释放同一 ID 不得影响其他连接
    assert disconnect_pair('C1', tables) is False
    assert set(tables.pairs) == {'C3', 'C5'}
