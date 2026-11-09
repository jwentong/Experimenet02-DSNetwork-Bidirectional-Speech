"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions


def _port(endpoint):
    return (endpoint.link_id, endpoint.timeslot)


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
    if _port(endpoint_a) == _port(endpoint_b):
        raise ValueError('连接两端不能是同一端口')
    if connection_id in tables.pairs:
        return False
    occupied = {_port(endpoint) for pair in tables.pairs.values() for endpoint in pair}
    if _port(endpoint_a) in occupied or _port(endpoint_b) in occupied:
        return False

    # 阶段一：只检查，不写表。每个方向各占一个T输出和一个S输出。
    planned = []
    t_keys, s_keys = set(), set()
    for src, dst in directions(endpoint_a, endpoint_b):
        t_key = (src.link_id, dst.timeslot)
        s_key = (dst.link_id, dst.timeslot)
        # T输出与S输出是两个独立的资源空间，(链路,时隙)相同的键不能互相顶替。
        if t_key[1] in tables.t_maps[t_key[0]] or s_key in tables.s_map or t_key in t_keys or s_key in s_keys:
            return False
        t_keys.add(t_key)
        s_keys.add(s_key)
        planned.append((src.link_id, dst.timeslot, src.timeslot, s_key, src.link_id))

    # 阶段二：两个方向全部通过后一起提交，保证原子性。
    for t_link, out_timeslot, in_timeslot, s_key, src_link in planned:
        tables.t_maps[t_link][out_timeslot] = in_timeslot
        tables.s_map[s_key] = src_link
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
    for src, dst in directions(pair[0], pair[1]):
        tables.t_maps[src.link_id].pop(dst.timeslot, None)
        tables.s_map.pop((dst.link_id, dst.timeslot), None)
    del tables.pairs[connection_id]
    return True
