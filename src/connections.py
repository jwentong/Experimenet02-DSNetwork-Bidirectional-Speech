"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)

    if endpoint_a == endpoint_b:
        raise ValueError("两端不能相同")

    if connection_id in tables.pairs:
        return False

    src1, dst1 = endpoint_a, endpoint_b
    src2, dst2 = endpoint_b, endpoint_a

    t_link1 = src1.link_id
    t_out_ts1 = dst1.timeslot
    s_key1 = (dst1.link_id, dst1.timeslot)

    t_link2 = src2.link_id
    t_out_ts2 = dst2.timeslot
    s_key2 = (dst2.link_id, dst2.timeslot)

    if t_out_ts1 in tables.t_maps[t_link1] or t_out_ts2 in tables.t_maps[t_link2]:
        return False
    if s_key1 in tables.s_map or s_key2 in tables.s_map:
        return False

    tables.t_maps[t_link1][t_out_ts1] = src1.timeslot
    tables.s_map[s_key1] = src1.link_id

    tables.t_maps[t_link2][t_out_ts2] = src2.timeslot
    tables.s_map[s_key2] = src2.link_id

    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    if connection_id not in tables.pairs:
        return False

    endpoint_a, endpoint_b = tables.pairs[connection_id]
    del tables.pairs[connection_id]

    src1, dst1 = endpoint_a, endpoint_b
    t_link1 = src1.link_id
    t_out_ts1 = dst1.timeslot
    s_key1 = (dst1.link_id, dst1.timeslot)
    if t_out_ts1 in tables.t_maps[t_link1]:
        del tables.t_maps[t_link1][t_out_ts1]
    if s_key1 in tables.s_map:
        del tables.s_map[s_key1]

    src2, dst2 = endpoint_b, endpoint_a
    t_link2 = src2.link_id
    t_out_ts2 = dst2.timeslot
    s_key2 = (dst2.link_id, dst2.timeslot)
    if t_out_ts2 in tables.t_maps[t_link2]:
        del tables.t_maps[t_link2][t_out_ts2]
    if s_key2 in tables.s_map:
        del tables.s_map[s_key2]

    return True
