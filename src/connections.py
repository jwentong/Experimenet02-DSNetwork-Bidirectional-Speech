"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions


def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。

    非法端口或两端相同抛ValueError。ID已存在、端口已占用、
    内部T输出或S输出资源冲突，返回False且tables完全不变。
    方向src→dst：T[src.link_id][dst.timeslot]=src.timeslot；
    S[(dst.link_id,dst.timeslot)]=src.link_id。
    两个方向全部检查通过才写表，并记录pairs[id]=(a,b)。
    本实验固定路径可能发生内部阻塞，不要求自动改走其他路径。
    """
    if validate_endpoint(endpoint_a) is False or validate_endpoint(endpoint_b) is False:
        raise ValueError("存在非法端点")
    if (endpoint_a.link_id, endpoint_a.timeslot) == (endpoint_b.link_id, endpoint_b.timeslot):
        raise ValueError("连接两端不能为同一端口")

    if connection_id in tables.pairs:
        return False

    new_ports = {
        (endpoint_a.link_id, endpoint_a.timeslot),
        (endpoint_b.link_id, endpoint_b.timeslot),
    }
    for ep_x, ep_y in tables.pairs.values():
        if (ep_x.link_id, ep_x.timeslot) in new_ports or (ep_y.link_id, ep_y.timeslot) in new_ports:
            return False

    dir_pairs = list(directions(endpoint_a, endpoint_b))
    for src, dst in dir_pairs:
        t_map = tables.t_maps[src.link_id]
        if dst.timeslot in t_map:
            return False
        if src.timeslot in t_map.values():
            return False
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False
        if (src.link_id, src.timeslot) in tables.s_map:
            return False

    for src, dst in dir_pairs:
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id

    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。

    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    if connection_id not in tables.pairs:
        return False

    endpoint_a, endpoint_b = tables.pairs.pop(connection_id)
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id].pop(dst.timeslot, None)
        tables.s_map.pop((dst.link_id, dst.timeslot), None)

    return True


