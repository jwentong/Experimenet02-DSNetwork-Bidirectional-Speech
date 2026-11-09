"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    if endpoint_a.link_id == endpoint_b.link_id and endpoint_a.timeslot == endpoint_b.timeslot:
        raise ValueError('两端不能是同一个端点')
    if connection_id in tables.pairs:
        return False
    dirs = directions(endpoint_a, endpoint_b)
    to_write = []
    for src, dst in dirs:
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False
        to_write.append((src, dst))
    for src, dst in to_write:
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    if connection_id not in tables.pairs:
        return False
    a, b = tables.pairs[connection_id]
    del tables.t_maps[a.link_id][b.timeslot]
    del tables.s_map[(b.link_id, b.timeslot)]
    del tables.t_maps[b.link_id][a.timeslot]
    del tables.s_map[(a.link_id, a.timeslot)]
    del tables.pairs[connection_id]
    return True
