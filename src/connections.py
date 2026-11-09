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
    if endpoint_a == endpoint_b:
        raise ValueError('两端不能是同一个端口')

    # 重复连接ID
    if connection_id in tables.pairs:
        return False

    # 端点独占：任何一个端点已被既有连接占用则拒绝
    occupied = set()
    for a, b in tables.pairs.values():
        occupied.add((a.link_id, a.timeslot))
        occupied.add((b.link_id, b.timeslot))
    if ((endpoint_a.link_id, endpoint_a.timeslot) in occupied
            or (endpoint_b.link_id, endpoint_b.timeslot) in occupied):
        return False

    # 内部资源冲突：每个方向占用的 T 输出与 S 输出都不能被覆盖
    for src, dst in directions(endpoint_a, endpoint_b):
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False

    # 全部检查通过，原子写入两个方向并登记连接
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
    if connection_id not in tables.pairs:
        return False
    a, b = tables.pairs.pop(connection_id)
    for src, dst in directions(a, b):
        del tables.t_maps[src.link_id][dst.timeslot]
        del tables.s_map[(dst.link_id, dst.timeslot)]
    return True
