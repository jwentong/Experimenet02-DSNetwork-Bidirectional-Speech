"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint


def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。
    非法端口或两端相同抛ValueError。ID已存在、端口已占用、
    内部T输出或S输出资源冲突，返回False且tables完全不变。
    方向src→dst：T[src.link_id][dst.timeslot]=src.timeslot；
    S[(dst.link_id,dst.timeslot)]=src.link_id。
    两个方向全部检查通过才写表，并记录pairs[id]=(a,b)。
    本实验固定路径可能发生内部阻塞，不要求自动改走其他路径。
    """
    # 1. 校验端点合法性，非法抛ValueError
    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)
    # 两端完全相同抛异常
    if (endpoint_a.link_id == endpoint_b.link_id) and (endpoint_a.timeslot == endpoint_b.timeslot):
        raise ValueError("两端端点不能完全相同")
    # 连接ID已经存在，直接返回False
    if connection_id in tables.pairs:
        return False

    a_link = endpoint_a.link_id
    a_ts = endpoint_a.timeslot
    b_link = endpoint_b.link_id
    b_ts = endpoint_b.timeslot

    # ========== 预检查（只读，不修改任何tables） ==========
    # A→B：t_maps[a_link][b_ts] ； s_map[(b_link, b_ts)]
    # B→A：t_maps[b_link][a_ts] ； s_map[(a_link, a_ts)]
    # t_maps[link] 是字典：key存在=时隙被占用
    t_conflict1 = b_ts in tables.t_maps[a_link]
    t_conflict2 = a_ts in tables.t_maps[b_link]

    s_conflict1 = (b_link, b_ts) in tables.s_map
    s_conflict2 = (a_link, a_ts) in tables.s_map

    # 任意资源冲突，直接返回False，不写任何表
    if t_conflict1 or t_conflict2 or s_conflict1 or s_conflict2:
        return False

    # ========== 全部校验通过，才执行写入 ==========
    # A → B
    tables.t_maps[a_link][b_ts] = a_ts
    tables.s_map[(b_link, b_ts)] = a_link
    # B → A
    tables.t_maps[b_link][a_ts] = b_ts
    tables.s_map[(a_link, a_ts)] = b_link

    # 登记双向连接对
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。
    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    # ID不存在直接返回False
    if connection_id not in tables.pairs:
        return False

    endpoint_a, endpoint_b = tables.pairs[connection_id]
    a_link = endpoint_a.link_id
    a_ts = endpoint_a.timeslot
    b_link = endpoint_b.link_id
    b_ts = endpoint_b.timeslot

    # 删除 A→B 资源：t_maps[link]是字典，用pop
    tables.t_maps[a_link].pop(b_ts, None)
    tables.s_map.pop((b_link, b_ts), None)

    # 删除 B→A 资源
    tables.t_maps[b_link].pop(a_ts, None)
    tables.s_map.pop((a_link, a_ts), None)

    # 删除连接记录
    del tables.pairs[connection_id]
    return True
