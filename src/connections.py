# src/connections.py

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    # ---------- 1) 参数校验 ----------
    def _check_ep(ep):
        if ep.link_id not in (0, 1):
            raise ValueError(f"illegal link: {ep.link_id!r}")
        if ep.timeslot < 1 or ep.timeslot > 31 or ep.timeslot == 16:
            raise ValueError(f"illegal timeslot: {ep.timeslot!r}")

    _check_ep(endpoint_a)
    _check_ep(endpoint_b)
    
    # 两端不能完全相同
    if endpoint_a.link_id == endpoint_b.link_id and endpoint_a.timeslot == endpoint_b.timeslot:
        raise ValueError("endpoints must differ")

    # ---------- 2) 重复 ID -> False ----------
    if connection_id in tables.pairs:
        return False

    # 提取属性，方便后续编写
    a_link = endpoint_a.link_id
    a_ts = endpoint_a.timeslot
    b_link = endpoint_b.link_id
    b_ts = endpoint_b.timeslot

    t_map = tables.t_maps
    s_map = tables.s_map

    # ---------- 3) 在副本上模拟检查，全部通过才落盘 ----------
    
    # 检查 T 表冲突（t_map 是列表，t_map[link] 是字典，用 in 判断键）
    if b_ts in t_map[a_link] or a_ts in t_map[b_link]:
        return False

    # 检查 S 表冲突（s_map 也是字典）
    if (b_link, b_ts) in s_map or (a_link, a_ts) in s_map:
        return False

    # ---------- 4) 全部通过，一次性写入 ----------
    
    # 写入 T 表
    t_map[a_link][b_ts] = a_ts
    t_map[b_link][a_ts] = b_ts
    
    # 写入 S 表
    s_map[(b_link, b_ts)] = a_link
    s_map[(a_link, a_ts)] = b_link
    
    # 登记 pairs
    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    
    return True


def disconnect_pair(connection_id, tables):
    # 未知或重复释放
    if connection_id not in tables.pairs:
        return False

    # 取回两端的 Endpoint 对象
    a, b = tables.pairs[connection_id]
    a_link = a.link_id
    a_ts = a.timeslot
    b_link = b.link_id
    b_ts = b.timeslot

    t_map = tables.t_maps
    s_map = tables.s_map

    # 删除 a -> b 方向
    if b_ts in t_map[a_link]:
        del t_map[a_link][b_ts]
    if (b_link, b_ts) in s_map:
        del s_map[(b_link, b_ts)]

    # 删除 b -> a 方向
    if a_ts in t_map[b_link]:
        del t_map[b_link][a_ts]
    if (a_link, a_ts) in s_map:
        del s_map[(a_link, a_ts)]

    # 删除 pairs 记录
    del tables.pairs[connection_id]
    
    return True