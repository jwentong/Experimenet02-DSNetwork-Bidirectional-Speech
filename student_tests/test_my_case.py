import numpy as np
from src.t_switch import t_switch
from src.models import IDLE

def test_my_t_switch_case():
    # 准备输入帧：全填 0
    input_frame = np.zeros(32, dtype=np.uint8)
    # 在输入 TS1 填入 11，在 TS3 填入 33
    input_frame[1] = 11
    input_frame[3] = 33
    
    # 控制表：输出 TS3 连输入 TS1，输出 TS1 连输入 TS3
    control_memory = {3: 1, 1: 3}
    
    # 调用实验函数
    output_frame = t_switch(input_frame, control_memory)
    
    # 断言：验证交换结果
    assert output_frame[1] == 33, "TS1 应当得到输入 TS3 的数据"
    assert output_frame[3] == 11, "TS3 应当得到输入 TS1 的数据"
    # 断言：验证未连接输出填了 IDLE
    assert output_frame[2] == IDLE, "未连接时隙应当填充 IDLE"