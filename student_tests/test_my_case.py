# student_tests/test_my_case.py

# 导入你写好的函数
from src.connections import connect_pair, disconnect_pair

# 为了让测试能独立运行，我们用简单的类模拟教师的 Endpoint 和 Tables
class FakeEndpoint:
    def __init__(self, link_id, timeslot):
        self.link_id = link_id
        self.timeslot = timeslot

class FakeTables:
    def __init__(self):
        # 根据之前报错探明的结构：t_maps 是包含 2 个字典的列表
        self.t_maps = [{}, {}]
        self.s_map = {}
        self.pairs = {}

def test_release_then_reuse():
    """
    测试目的：验证连接释放后，原本占用的内部资源可以被重新使用。
    输入：
        建立 C1 连接 A(0,1) 到 B(1,5)
        释放 C1
        建立 C3 连接 A(0,1) 到 B(1,5)（使用同样的端点）
    预期：
        C1 建立成功 (True)
        C1 释放成功 (True)
        重复释放 C1 失败 (False)
        C3 建立成功 (True)
    """
    tables = FakeTables()
    A = FakeEndpoint(0, 1)
    B = FakeEndpoint(1, 5)

    # 1. 建立连接 C1
    assert connect_pair("C1", A, B, tables) is True
    # 检查 T 表是否写入成功
    assert tables.t_maps[0][5] == 1
    assert tables.t_maps[1][1] == 5

    # 2. 释放连接 C1
    assert disconnect_pair("C1", tables) is True
    # 检查 T 表是否已清空
    assert 5 not in tables.t_maps[0]
    assert 1 not in tables.t_maps[1]

    # 3. 重复释放应返回 False
    assert disconnect_pair("C1", tables) is False

    # 4. 重用刚才释放的资源建立新连接 C3
    assert connect_pair("C3", A, B, tables) is True
    assert tables.t_maps[0][5] == 1