from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    # 1. 校验端点合法性（如果非法会抛出 ValueError）
    # 老师提供的函数会检查是否在0/1链路，是否为TS1-31（排除TS16）
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    
    # 2. 检查两端是否物理相同
    if endpoint_a.link_id == endpoint_b.link_id and endpoint_a.timeslot == endpoint_b.timeslot:
        raise ValueError("Endpoints must be different")
        
    # 3. 检查 ID 是否已经存在
    if connection_id in tables.pairs:
        return False
        
    # 4. 检查端点是否已经被其他连接占用
    occupied = set()
    for a, b in tables.pairs.values():
        occupied.add((a.link_id, a.timeslot))
        occupied.add((b.link_id, b.timeslot))
        
    if (endpoint_a.link_id, endpoint_a.timeslot) in occupied or \
       (endpoint_b.link_id, endpoint_b.timeslot) in occupied:
        return False
        
    # 5. 检查内部 T 和 S 资源冲突（遍历 A->B 和 B->A 两个方向）
    for src, dst in directions(endpoint_a, endpoint_b):
        # 检查 T 表：src 链路，dst 时隙是否已被占用
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        # 检查 S 表：dst 链路，dst 时隙是否已被占用
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False
            
    # 6. 全部检查通过后，一次性原子写入表项
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id
        
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    # 1. 检查连接是否存在，未知或重复释放返回 False
    if connection_id not in tables.pairs:
        return False
        
    a, b = tables.pairs[connection_id]
    
    # 2. 删除两个方向的 T 表和 S 表映射
    for src, dst in directions(a, b):
        if dst.timeslot in tables.t_maps[src.link_id]:
            del tables.t_maps[src.link_id][dst.timeslot]
        if (dst.link_id, dst.timeslot) in tables.s_map:
            del tables.s_map[(dst.link_id, dst.timeslot)]
            
    # 3. 删除记录
    del tables.pairs[connection_id]
    return True