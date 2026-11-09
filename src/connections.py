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
    # Validate both ports before inspecting or mutating resource tables.
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    if endpoint_a == endpoint_b:
        raise ValueError('双向连接的两个端点必须不同')

    if connection_id in tables.pairs:
        return False

    occupied_endpoints = {
        endpoint
        for pair in tables.pairs.values()
        for endpoint in pair
    }
    if endpoint_a in occupied_endpoints or endpoint_b in occupied_endpoints:
        return False

    # Build all requested entries first, then check every resource before commit.
    pending_t = []
    pending_s = []
    for src, dst in directions(endpoint_a, endpoint_b):
        pending_t.append((src.link_id, dst.timeslot, src.timeslot))
        pending_s.append(((dst.link_id, dst.timeslot), src.link_id))

    if any(out_slot in tables.t_maps[link_id]
           for link_id, out_slot, _ in pending_t):
        return False
    if any(out_port in tables.s_map for out_port, _ in pending_s):
        return False

    for link_id, out_slot, in_slot in pending_t:
        tables.t_maps[link_id][out_slot] = in_slot
    for out_port, in_link in pending_s:
        tables.s_map[out_port] = in_link
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。

    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    pair = tables.pairs.get(connection_id)
    if pair is None:
        return False

    endpoint_a, endpoint_b = pair
    for src, dst in directions(endpoint_a, endpoint_b):
        # Remove only this connection's entries, leaving any unrelated entries intact.
        t_map = tables.t_maps[src.link_id]
        if t_map.get(dst.timeslot) == src.timeslot:
            del t_map[dst.timeslot]
        s_port = (dst.link_id, dst.timeslot)
        if tables.s_map.get(s_port) == src.link_id:
            del tables.s_map[s_port]
    del tables.pairs[connection_id]
    return True
