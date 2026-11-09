"""
自拟测试用例：T‑S交换网络双向话路
文件名：test_my_case.py
满足要求：存在test_函数，包含assert，可正常运行
"""
import numpy as np
import pytest
from src.t_switch import t_switch
from src.s_switch import s_switch
from src.models import IDLE, SLOTS

def test_t_switch_keep_ts0_ts16():
    """T接线器：TS0、TS16强制透传，不交换"""
    in_frame = np.arange(SLOTS, dtype=np.uint8)
    t_map = {3: 10}
    out = t_switch(in_frame, t_map)
    assert out[0] == in_frame[0]
    assert out[16] == in_frame[16]

def test_t_switch_idle_for_unmapped():
    """T接线器未映射时隙输出IDLE"""
    in_frame = np.zeros(SLOTS, dtype=np.uint8)
    t_map = {5:2}
    out = t_switch(in_frame, t_map)
    assert out[7] == IDLE

def test_s_switch_reject_ts0():
    """S接线器：禁止对TS0建立映射，预期抛ValueError"""
    n_link = 2
    frame = np.zeros((n_link, SLOTS), dtype=np.uint8)
    bad_map = {(0, 0): 1}
    with pytest.raises(ValueError):
        s_switch(frame, bad_map)

def test_s_switch_reject_ts16():
    """S接线器禁止映射TS16"""
    n_link = 2
    frame = np.zeros((n_link, SLOTS), dtype=np.uint8)
    bad_map = {(1,16):0}
    with pytest.raises(ValueError):
        s_switch(frame, bad_map)

def test_s_switch_data_copy_correct():
    """S交换时隙不变，跨链路拷贝数据"""
    n_link = 2
    frame = np.zeros((n_link, SLOTS), dtype=np.uint8)
    frame[1,5] = 0xAA
    s_map = {(0,5):1}
    out = s_switch(frame, s_map)
    assert out[0,5] == 0xAA
