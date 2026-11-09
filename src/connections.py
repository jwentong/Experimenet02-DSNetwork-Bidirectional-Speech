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
        raise ValueError("连接两端不能是同一个端口")

    if connection_id in tables.pairs:
        return False

    occupied=set()
    for old_a,old_b in tables.pairs.values():
        occupied.add((old_a.link_id,old_a.timeslot))
        occupied.add((old_b.link_id,old_b.timeslot))
    if (endpoint_a.link_id,endpoint_a.timeslot) in occupied or (endpoint_b.link_id,endpoint_b.timeslot) in occupied:
        return False

    planned=[]
    for src,dst in directions(endpoint_a,endpoint_b):
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        s_key=(dst.link_id,dst.timeslot)
        if s_key in tables.s_map:
            return False
        planned.append((src,dst,s_key))

    for src,dst,s_key in planned:
        tables.t_maps[src.link_id][dst.timeslot]=src.timeslot
        tables.s_map[s_key]=src.link_id
    tables.pairs[connection_id]=(endpoint_a,endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。

    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    pair=tables.pairs.get(connection_id)
    if pair is None:
        return False

    endpoint_a,endpoint_b=pair
    for src,dst in directions(endpoint_a,endpoint_b):
        tables.t_maps[src.link_id].pop(dst.timeslot,None)
        tables.s_map.pop((dst.link_id,dst.timeslot),None)
    del tables.pairs[connection_id]
    return True
