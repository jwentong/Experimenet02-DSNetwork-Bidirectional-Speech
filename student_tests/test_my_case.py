"""自拟反例：验证T-S交换内部阻塞与connect_pair原子性"""
from src.models import Tables, Endpoint
from src.connections import connect_pair


def test_internal_block_atomic():
    tbl = Tables()
    # 第一条连接：链路0时隙1 <--> 链路1时隙5
    ep_a1 = Endpoint(link_id=0, timeslot=1)
    ep_b1 = Endpoint(link_id=1, timeslot=5)
    res1 = connect_pair("C1", ep_a1, ep_b1, tbl)
    assert res1 is True

    # 保存当前控制表快照，用于校验原子性
    t_snapshot = [dict(item) for item in tbl.t_maps]
    s_snapshot = dict(tbl.s_map)

    # 尝试新建第二条连接：链路0时隙2 <--> 链路0时隙5
    ep_a2 = Endpoint(link_id=0, timeslot=2)
    ep_b2 = Endpoint(link_id=0, timeslot=5)
    res2 = connect_pair("C2", ep_a2, ep_b2, tbl)

    # 预期：冲突，返回False，两张表完全不变（原子性）
    assert res2 is False
    assert [dict(item) for item in tbl.t_maps] == t_snapshot
    assert dict(tbl.s_map) == s_snapshot
