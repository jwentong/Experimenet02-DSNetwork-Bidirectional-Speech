"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。"""
    # 1. 校验两端是否相同
    if endpoint_a == endpoint_b:
        raise ValueError("Endpoints cannot be the same")
        
    # 2. 校验端口合法性
    for ep in (endpoint_a, endpoint_b):
        # 为防止 validate_endpoint 不抛异常，这里加上硬校验
        if getattr(ep, 'link_id', -1) not in (0, 1) or \
           getattr(ep, 'timeslot', -1) in (0, 16) or \
           not (1 <= getattr(ep, 'timeslot', -1) < 32):
            raise ValueError("Invalid endpoint")
        validate_endpoint(ep)
        
    # 3. 检查 ID 是否重复
    if connection_id in tables.pairs:
        return False
        
    # 4. 检查端点是否被占用
    for existing_a, existing_b in tables.pairs.values():
        if endpoint_a in (existing_a, existing_b) or endpoint_b in (existing_a, existing_b):
            return False
            
    # 5. 检查内部 T 输出冲突 和 S 输出冲突
    for src, dst in directions(endpoint_a, endpoint_b):
        # 内部 T 输出冲突：该链路的该时隙是否已被占用
        if dst.timeslot in tables.t_maps[src.link_id]:
            return False
        # S 输出冲突：(目标链路, 目标时隙) 是否已被占用
        if (dst.link_id, dst.timeslot) in tables.s_map:
            return False
            
    # 6. 所有检查通过，原子写入映射表
    for src, dst in directions(endpoint_a, endpoint_b):
        tables.t_maps[src.link_id][dst.timeslot] = src.timeslot
        tables.s_map[(dst.link_id, dst.timeslot)] = src.link_id
        
    # 7. 记录连接对
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。"""
    if connection_id not in tables.pairs:
        return False
        
    a, b = tables.pairs[connection_id]
    
    # 删除两个方向的 T 表和 S 表映射
    for src, dst in directions(a, b):
        del tables.t_maps[src.link_id][dst.timeslot]
        del tables.s_map[(dst.link_id, dst.timeslot)]
        
    # 删除连接记录
    del tables.pairs[connection_id]
    return True