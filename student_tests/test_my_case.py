import numpy as np
from src.models import Endpoint, Tables
from src.t_switch import t_switch
from src.connections import connect_pair, disconnect_pair

def test_t_swap_and_no_mutation():
    # 手算用例：TS1=11, TS3=33
    frame = np.full(32, 0xD5, dtype=np.uint8)
    frame[1] = 11
    frame[3] = 33
    
    # 换时隙
    out = t_switch(frame, {1: 3, 3: 1})
    assert out[1] == 33
    assert out[3] == 11
    assert frame[1] == 11  # 原输入不变

def test_connect_conflict_and_release():
    tables = Tables()
    a = Endpoint(link_id=0, timeslot=1)
    b = Endpoint(link_id=1, timeslot=5)
    
    # 1. 建立连接
    assert connect_pair("C1", a, b, tables) is True
    
    # 2. 内部冲突测试 (C1存在时，请求写 T0[5] 必须失败)
    c = Endpoint(link_id=0, timeslot=2)
    d = Endpoint(link_id=0, timeslot=5)
    assert connect_pair("C2", c, d, tables) is False
    
    # 3. 释放 C1
    assert disconnect_pair("C1", tables) is True
    
    # 4. 释放后，C2 资源可重用建立成功
    assert connect_pair("C2", c, d, tables) is True