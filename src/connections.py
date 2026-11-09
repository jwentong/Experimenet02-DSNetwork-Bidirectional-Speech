
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

    # 1. 检查两个端点是否合法
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)

    # 2. 不允许两个端点相同
    if (endpoint_a.link_id == endpoint_b.link_id and
            endpoint_a.timeslot == endpoint_b.timeslot):
        raise ValueError("双向连接的两个端点不能相同")

    # 3. 检查连接ID是否已经存在
    if connection_id in tables.pairs:
        return False

    # 4. 检查两个端点是否已被其他连接占用
    for a, b in tables.pairs.values():
        occupied = {
            (a.link_id, a.timeslot),
            (b.link_id, b.timeslot)
        }

        if ((endpoint_a.link_id, endpoint_a.timeslot) in occupied or
                (endpoint_b.link_id, endpoint_b.timeslot) in occupied):
            return False

    # 5. 检查两个方向的内部T/S资源是否冲突
    for src, dst in directions(endpoint_a, endpoint_b):

        # T交换资源：(输入链路, 输出时隙)
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False

        # S交换资源：(输出链路, 输出时隙)
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False

    # 6. 所有检查通过，正式建立两个方向的映射
    for src, dst in directions(endpoint_a, endpoint_b):

        # T交换：在输入链路上改变时隙
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot

        # S交换：在目的时隙上切换到输出链路
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id

    # 7. 记录连接ID及两个端点
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)

    return True



def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。

    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """

    # 1. 检查连接ID是否存在
    if connection_id not in tables.pairs:
        return False

    # 2. 获取该连接的两个端点
    endpoint_a, endpoint_b = tables.pairs[connection_id]

    # 3. 释放两个方向的T交换和S交换资源
    for src, dst in directions(endpoint_a, endpoint_b):

        # 删除T交换映射
        tables.t_maps[src.link_id].pop(dst.timeslot, None)

        # 删除S交换映射
        tables.s_map.pop((dst.link_id, dst.timeslot), None)

    # 4. 删除连接记录
    del tables.pairs[connection_id]

    # 5. 释放成功
    return True

