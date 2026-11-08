"""任务三与四：双向连接控制与释放。"""
from numbers import Integral
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
    for endpoint in (endpoint_a, endpoint_b):
        if any(not isinstance(value, Integral) or isinstance(value, bool)
               for value in (endpoint.link_id, endpoint.timeslot)):
            raise ValueError('端口的链路号与时隙号必须为整数')
        validate_endpoint(endpoint)
    if endpoint_a == endpoint_b:
        raise ValueError('双向连接必须使用两个不同端口')
    if connection_id in tables.pairs:
        return False

    for pair in tables.pairs.values():
        if endpoint_a in pair or endpoint_b in pair:
            return False

    routes = directions(endpoint_a, endpoint_b)
    for src, dst in routes:
        if (dst.timeslot in tables.t_maps[src.link_id]
                or (dst.link_id, dst.timeslot) in tables.s_map):
            return False

    # 两个方向都可用后再提交，拒绝连接不会留下半条话路。
    for src, dst in routes:
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

    endpoint_a, endpoint_b = tables.pairs[connection_id]
    for src, dst in directions(endpoint_a, endpoint_b):
        del tables.t_maps[src.link_id][dst.timeslot]
        del tables.s_map[(dst.link_id, dst.timeslot)]
    del tables.pairs[connection_id]
    return True
