import numpy as np
from src.t_switch import t_switch
from src.models import IDLE

def test_my_custom_t_switch():
    # 构造一个带有特定值的输入帧
    frame = np.zeros(32, dtype=np.uint8)
    frame[2] = 88
    frame[0] = 1
    frame[16] = 2
    
    # 设定映射：输出时隙 25 指向输入时隙 2
    control_memory = {25: 2}
    
    # 执行 T 交换
    result = t_switch(frame, control_memory)
    
    # 断言：25号时隙应该拿到2号时隙的值88
    assert result[25] == 88
    # 断言：保留位透传，未连接填IDLE
    assert result[0] == 1
    assert result[16] == 2
    assert result[1] == IDLE