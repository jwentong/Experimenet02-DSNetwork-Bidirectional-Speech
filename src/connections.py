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
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    if (endpoint_a.link_id, endpoint_a.timeslot) == (endpoint_b.link_id, endpoint_b.timeslot):
        raise ValueError('一条连接的两端不能是同一个端口')
    if connection_id in tables.pairs:
        return False
    # 两个方向全部检查通过才写表；任一冲突立即整体拒绝，tables保持原样。
    for src, dst in directions(endpoint_a, endpoint_b):
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False                        # 内部T输出已被占用（固定路径阻塞）
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False                        # 目的端口已被占用，或内部S输出冲突
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id
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
    for src, dst in directions(*pair):
        tables.t_maps[src.link_id].pop(dst.timeslot, None)
        tables.s_map.pop((dst.link_id, dst.timeslot), None)
    del tables.pairs[connection_id]
    return True
