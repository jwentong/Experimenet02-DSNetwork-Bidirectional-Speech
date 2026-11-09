"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。..."""
    
    # 1. 非法端口检查（如果内部抛出ValueError就直接抛出）
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    
    # 两端相同抛ValueError
    if endpoint_a.link_id == endpoint_b.link_id and endpoint_a.timeslot == endpoint_b.timeslot:
        raise ValueError("两端点不能相同")

    # 2. 检查重复 ID
    if connection_id in tables.pairs:
        return False

    # 3. 检查端点是否已被占用
    for a, b in tables.pairs.values():
        for new_ep in (endpoint_a, endpoint_b):
            if (new_ep.link_id == a.link_id and new_ep.timeslot == a.timeslot) or \
               (new_ep.link_id == b.link_id and new_ep.timeslot == b.timeslot):
                return False

    # 4. 检查内部 T 和 S 资源冲突
    for src, dst in directions(endpoint_a, endpoint_b):
        # T 表冲突：目标时隙是否已被占用
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        # S 表冲突：目标链路和时隙是否已被占用
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False

    # 5. 全部检查通过，一次性写入表
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id

    # 记录 pair
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。..."""
    
    # 1. 检查 ID 是否存在
    if connection_id not in tables.pairs:
        return False

    # 2. 获取两端
    a, b = tables.pairs[connection_id]

    # 3. 删除两个方向的控制表记录
    for src, dst in directions(a, b):
        del tables.t_maps[src.link_id][dst.timeslot]
        del tables.s_map[(dst.link_id, dst.timeslot)]

    # 4. 删除 pairs 记录
    del tables.pairs[connection_id]

    return True