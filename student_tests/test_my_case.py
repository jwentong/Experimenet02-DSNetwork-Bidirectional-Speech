
"""自拟测试：验证双向连接释放后不影响其他连接，且资源可重用。"""

from src.models import Endpoint, Tables
from src.connections import connect_pair, disconnect_pair


def test_release_and_reuse():
    # 创建一组空的交换控制表
    tables = Tables()

    # 定义两组双向连接
    a = Endpoint(0, 1)
    b = Endpoint(1, 5)

    c = Endpoint(0, 2)
    d = Endpoint(1, 6)

    # 1. 建立两组双向连接
    assert connect_pair("C1", a, b, tables) is True
    assert connect_pair("C2", c, d, tables) is True

    # 2. 检查两组连接均已登记
    assert "C1" in tables.pairs
    assert "C2" in tables.pairs

    # 3. 释放第一组连接
    assert disconnect_pair("C1", tables) is True

    # 4. 检查C1已删除，但C2不受影响
    assert "C1" not in tables.pairs
    assert "C2" in tables.pairs

    # 5. 检查C2的T/S映射仍然存在
    assert tables.t_maps[0][6] == 2
    assert tables.t_maps[1][2] == 6
    assert tables.s_map[(1, 6)] == 0
    assert tables.s_map[(0, 2)] == 1

    # 6. 验证C1的资源已经释放
    assert 5 not in tables.t_maps[0]
    assert 1 not in tables.t_maps[1]
    assert (1, 5) not in tables.s_map
    assert (0, 1) not in tables.s_map

    # 7. 使用原来的端点重新建立新连接
    assert connect_pair("C3", a, b, tables) is True

    # 8. 检查资源重用成功
    assert "C3" in tables.pairs
    assert "C2" in tables.pairs

    # 9. 检查重复释放已不存在的C1会被拒绝
    assert disconnect_pair("C1", tables) is False
