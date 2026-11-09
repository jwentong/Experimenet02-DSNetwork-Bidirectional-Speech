"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions


def _validate_endpoint(endpoint):
    try:
        validate_endpoint(endpoint)
    except (AttributeError, TypeError) as exc:
        raise ValueError('端点必须包含合法的链路号和时隙号') from exc


def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。

    非法端口或两端相同抛ValueError。ID已存在、端口已占用、
    内部T输出或S输出资源冲突，返回False且tables完全不变。
    方向src→dst：T[src.link_id][dst.timeslot]=src.timeslot；
    S[(dst.link_id,dst.timeslot)]=src.link_id。
    两个方向全部检查通过才写表，并记录pairs[id]=(a,b)。
    本实验固定路径可能发生内部阻塞，不要求自动改走其他路径。
    """
    _validate_endpoint(endpoint_a)
    _validate_endpoint(endpoint_b)

    position_a = (endpoint_a.link_id, endpoint_a.timeslot)
    position_b = (endpoint_b.link_id, endpoint_b.timeslot)
    if position_a == position_b:
        raise ValueError('双向连接的两端不能是同一个端点')
    if connection_id in tables.pairs:
        return False

    # 一对端点占用两端。先按pairs检查，避免依赖某一个方向的表项推断占用。
    used_endpoints = {
        (endpoint.link_id, endpoint.timeslot)
        for pair in tables.pairs.values()
        for endpoint in pair
    }
    if position_a in used_endpoints or position_b in used_endpoints:
        return False

    # 控制表也必须独立检查：源时隙和目的输出键即使值恰好是IDLE也仍算占用。
    for endpoint in (endpoint_a, endpoint_b):
        if endpoint.timeslot in tables.t_maps[endpoint.link_id].values():
            return False
        if (endpoint.link_id, endpoint.timeslot) in tables.s_map:
            return False

    for source, destination in directions(endpoint_a, endpoint_b):
        if destination.timeslot in tables.t_maps[source.link_id]:
            return False
        if (destination.link_id, destination.timeslot) in tables.s_map:
            return False

    # 到这里才修改教师提供的控制表，使拒绝操作保持原子性。
    for source, destination in directions(endpoint_a, endpoint_b):
        tables.t_maps[source.link_id][destination.timeslot] = source.timeslot
        tables.s_map[(destination.link_id, destination.timeslot)] = source.link_id
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。

    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    if connection_id not in tables.pairs:
        return False

    endpoint_a, endpoint_b = tables.pairs[connection_id]
    for source, destination in directions(endpoint_a, endpoint_b):
        tables.t_maps[source.link_id].pop(destination.timeslot, None)
        tables.s_map.pop((destination.link_id, destination.timeslot), None)
    del tables.pairs[connection_id]
    return True
