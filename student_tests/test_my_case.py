"""自拟测试：T/S 资源按链路区分，且冲突拒绝必须原子。

手算基准：
  连接 A=(0,1)-(1,5) 后控制表为 T0{5:1}、T1{1:5}、S{(1,5):0,(0,1):1}。
  此时 (0,2)-(0,5) 前向需要 T0[5]=2，与 A 的 T0[5]=1 冲突，必须整体拒绝；
  但 (1,2)-(0,5) 只需要 T1[5]=2 与 S[(0,5)]=1，链路 1 的 T 表未被占用，
  所以应当允许——说明 T 资源按“输入链路”区分，不能只按时隙号全局判重。
"""
from copy import deepcopy

import numpy as np

from src.models import Endpoint as E, Tables, IDLE
from src.connections import connect_pair, disconnect_pair
from src.engine import sample_frame, exchange_frame


def test_same_slot_different_link_is_not_a_conflict():
    tables = Tables()
    assert connect_pair('A', E(0, 1), E(1, 5), tables) is True
    old = deepcopy(tables)

    # 同一时隙号 5，但占用的是链路 0 的 T 输出，因此这条必须被拒绝
    assert connect_pair('B', E(0, 2), E(0, 5), tables) is False
    assert tables == old

    # 走链路 1 的 T 表和链路 0 的 S 表，资源各自空闲，应当成功
    assert connect_pair('C', E(1, 2), E(0, 5), tables) is True
    assert tables.t_maps[1][5] == 2 and tables.s_map[(0, 5)] == 1
    assert tables.t_maps[0][5] == 1          # A 的表项没有被改动

    frame = sample_frame(0)
    out = exchange_frame(frame, tables)
    assert out[0, 5] == frame[1, 2]          # C 的 forward 方向
    assert out[1, 5] == frame[0, 1]          # A 仍在正常传送


def test_release_frees_port_for_reuse():
    tables = Tables()
    assert connect_pair('A', E(0, 1), E(1, 5), tables)
    assert disconnect_pair('A', tables) is True
    assert tables == Tables()

    frame = sample_frame(1)
    out = exchange_frame(frame, tables)
    assert out[1, 5] == IDLE and out[0, 1] == IDLE   # 未连接输出回到空闲

    # 同一对端口可以重新建立连接，字节恢复传送
    assert connect_pair('A2', E(0, 1), E(1, 5), tables) is True
    out2 = exchange_frame(frame, tables)
    assert out2[1, 5] == frame[0, 1] and out2[0, 1] == frame[1, 5]
