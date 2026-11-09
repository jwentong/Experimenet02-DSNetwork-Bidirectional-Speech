"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T->S映射，成功返回True。"""
    # 1. 非法端口或两端相同抛 ValueError
    if endpoint_a == endpoint_b:
        raise ValueError("两端不能相同")
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    
    # 2. 重复ID返回False
    if connection_id in tables.pairs:
        return False
        
    # 3. 检查所有方向和所有资源是否冲突
    for src, dst in directions(endpoint_a, endpoint_b):
        # T表冲突：目标时隙已被该输入链路使用（内部阻塞）
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        # S表冲突：目标链路的目标时隙已被使用
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False
        # 端点占用：源端点已被占用（作为源在T表值中，或作为目标在S表中）
        if src.timeslot in tables.t_maps[src.link_id].values() or (src.link_id, src.timeslot) in tables.s_map:
            return False

    # 4. 全部检查通过，执行原子写入
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id
        
    # 记录连接对
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。"""
    # 未知ID返回False
    if connection_id not in tables.pairs:
        return False
        
    a, b = tables.pairs[connection_id]
    
    # 遍历两个方向，清除T表和S表
    for src, dst in directions(a, b):
        # 删除 T 表项
        if dst.timeslot in tables.t_maps[src.link_id]:
            del tables.t_maps[src.link_id][dst.timeslot]
        # 删除 S 表项
        if (dst.link_id, dst.timeslot) in tables.s_map:
            del tables.s_map[(dst.link_id, dst.timeslot)]
            
    # 删除 pairs 记录
    del tables.pairs[connection_id]
    return True