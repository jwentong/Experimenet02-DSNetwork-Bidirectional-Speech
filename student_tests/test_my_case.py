"""自拟反例：反向话路逐字节、内部T输出阻塞、释放后资源重用。

手算依据 sample_frame(k)[link,slot]=(link*101+slot*3+k*17)%256。
取k=3时链路0的TS4为63、链路1的TS9为179，用于核对两个方向没有互相串线。
"""
import numpy as np
from src.models import Endpoint as E, Tables, snapshot, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame

def test_reverse_direction_bytes_and_reserved():
    """C=(0,4)↔D=(1,9)：两个方向各自取对端字节，保留时隙仍原位透传。"""
    t = Tables()
    a, b = E(0, 4), E(1, 9)
    assert connect_pair('R1', a, b, t) is True
    assert t.t_maps == [{9: 4}, {4: 9}] and t.s_map == {(1, 9): 0, (0, 4): 1}
    frame = sample_frame(3)
    assert int(frame[0, 4]) == 63 and int(frame[1, 9]) == 179
    out = exchange_frame(frame, t)
    assert int(out[1, 9]) == 63          # (0,4)→(1,9)：改链路由T0输出TS9再选S(1,9)
    assert int(out[0, 4]) == 179         # (1,9)→(0,4)：反方向独立
    assert int(out[0, 7]) == IDLE        # 未连接业务输出为空闲
    assert int(out[0, 0]) == int(frame[0, 0]) and int(out[1, 16]) == int(frame[1, 16])

def test_internal_t_block_keeps_tables():
    """C1占用T0输出TS5后，请求(0,3)与(0,5)虽端点空闲仍须整体拒绝。"""
    t = Tables()
    assert connect_pair('C1', E(0, 1), E(1, 5), t) is True
    before = snapshot(t)
    assert connect_pair('C2', E(0, 3), E(0, 5), t) is False
    assert snapshot(t) == before
    frame = sample_frame(0)
    assert int(exchange_frame(frame, t)[1, 5]) == int(frame[0, 1])   # 原连接继续传送

def test_release_then_reuse_same_endpoints():
    """释放后T/S表项一起消失，输出回到IDLE，资源可被新连接重新占用。"""
    t = Tables()
    a, b = E(0, 4), E(1, 9)
    assert connect_pair('R1', a, b, t) is True
    assert disconnect_pair('R1', t) is True
    assert t.t_maps == [{}, {}] and t.s_map == {} and t.pairs == {}
    frame = sample_frame(0)
    out = exchange_frame(frame, t)
    assert int(out[1, 9]) == IDLE and int(out[0, 4]) == IDLE
    assert connect_pair('R2', a, b, t) is True
    assert int(exchange_frame(frame, t)[1, 9]) == int(frame[0, 4])
