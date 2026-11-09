"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions


def _point(endpoint):
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
    if _point(endpoint_a) == _point(endpoint_b):
        raise ValueError('两端不能是同一个端口')

    if connection_id in tables.pairs:
        return False

    # 端口占用按(链路,时隙)识别，字节值等于IDLE不代表端口空闲。
    busy = {point for pair in tables.pairs.values() for point in (_point(pair[0]), _point(pair[1]))}
    if _point(endpoint_a) in busy or _point(endpoint_b) in busy:
        return False

    # 内部资源：每个方向独占一个T输出(输入链路,目的时隙)和一个S输出(输出链路,时隙)。
    plan = []
    new_t_outputs, new_s_outputs = set(), set()
    for src, dst in directions(endpoint_a, endpoint_b):
        t_output = (src.link_id, dst.timeslot)
        s_output = (dst.link_id, dst.timeslot)
        if dst.timeslot in tables.t_maps[src.link_id] or s_output in tables.s_map:
            return False
        if t_output in new_t_outputs or s_output in new_s_outputs:
            return False
        new_t_outputs.add(t_output)
        new_s_outputs.add(s_output)
        plan.append((src, dst, s_output))

    # 两个方向全部通过后才一次性写入，失败时tables保持原样。
    for src, dst, s_output in plan:
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[s_output] = src.link_id
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
