"""任务三与四：双向连接控制与释放。"""
from numbers import Integral

from src.models import Endpoint, directions, validate_endpoint

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
        if not isinstance(endpoint, Endpoint) or any(
            not isinstance(value, Integral) or isinstance(value, bool)
            for value in (endpoint.link_id, endpoint.timeslot)
        ):
            raise ValueError("端口必须使用整数链路号和时隙号")
        validate_endpoint(endpoint)
    if endpoint_a == endpoint_b:
        raise ValueError("双向连接的两个端口必须不同")

    if connection_id in tables.pairs or any(
        endpoint_a in pair or endpoint_b in pair for pair in tables.pairs.values()
    ):
        return False

    paths = directions(endpoint_a, endpoint_b)
    for source, destination in paths:
        if (
            destination.timeslot in tables.t_maps[source.link_id]
            or (destination.link_id, destination.timeslot) in tables.s_map
        ):
            return False

    for source, destination in paths:
        tables.t_maps[source.link_id][destination.timeslot] = source.timeslot
        tables.s_map[(destination.link_id, destination.timeslot)] = source.link_id
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

    for source, destination in directions(*pair):
        tables.t_maps[source.link_id].pop(destination.timeslot, None)
        tables.s_map.pop((destination.link_id, destination.timeslot), None)
    del tables.pairs[connection_id]
    return True
