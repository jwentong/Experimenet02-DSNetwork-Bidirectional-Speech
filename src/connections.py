def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """
    原地建立双向T→S映射，成功返回True。
    非法端口或两端相同抛ValueError。ID已存在、端口已占用、
    内部T输出或S输出资源冲突，返回False且tables完全不变。
    方向 src→dst: T[src.link_id][dst.timeslot]=src.timeslot;
    S[(dst.link_id,dst.timeslot)]=src.link_id。
    两个方向全部检查通过才写表，并记录pairs[id]=(a,b)。
    本实验固定路径可能发生内部阻塞，不要求自动改走其他路径。
    """
    t_maps, s_map, pairs = tables.t_maps, tables.s_map, tables.pairs

    a_link = endpoint_a.link_id
    a_ts = endpoint_a.timeslot
    b_link = endpoint_b.link_id
    b_ts = endpoint_b.timeslot

    # 测试要求：E(0,0) 本身就是非法端点（时隙0不允许使用）
    if a_ts == 0 or b_ts == 0:
        raise ValueError("invalid endpoint")
    if a_link not in (0, 1) or b_link not in (0, 1):
        raise ValueError("invalid link")
    if a_link == b_link and a_ts == b_ts:
        raise ValueError("same endpoint")

    if not (0 <= a_ts < 32 and 0 <= b_ts < 32):
        raise ValueError("invalid timeslot")

    if connection_id in pairs:
        return False

    src1_link, src1_ts = a_link, a_ts
    dst1_link, dst1_ts = b_link, b_ts

    src2_link, src2_ts = b_link, b_ts
    dst2_link, dst2_ts = a_link, a_ts

    t1_conflict = dst1_ts in t_maps[src1_link]
    s1_conflict = (dst1_link, dst1_ts) in s_map

    t2_conflict = dst2_ts in t_maps[src2_link]
    s2_conflict = (dst2_link, dst2_ts) in s_map

    if t1_conflict or s1_conflict or t2_conflict or s2_conflict:
        return False

    t_maps[src1_link][dst1_ts] = src1_ts
    s_map[(dst1_link, dst1_ts)] = src1_link

    t_maps[src2_link][dst2_ts] = src2_ts
    s_map[(dst2_link, dst2_ts)] = src2_link

    pairs[connection_id] = (endpoint_a, endpoint_b)
    return True

def disconnect_pair(connection_id, tables):
    """
    根据连接id断开双向连接：
    - 找到 pair 保存的两个端点 a,b
    - 删除两条方向对应的 T 表项、S 表项
    - 从pairs字典删掉这条连接记录
    成功返回True；id不存在直接返回False，表不改动
    """
    t_maps, s_map, pairs = tables.t_maps, tables.s_map, tables.pairs
    if connection_id not in pairs:
        return False

    endpoint_a, endpoint_b = pairs[connection_id]
    a_link, a_ts = endpoint_a.link_id, endpoint_a.timeslot
    b_link, b_ts = endpoint_b.link_id, endpoint_b.timeslot

    # a -> b 方向
    del t_maps[a_link][b_ts]
    del s_map[(b_link, b_ts)]
    # b -> a 方向
    del t_maps[b_link][a_ts]
    del s_map[(a_link, a_ts)]

    del pairs[connection_id]
    return True

def lookup(endpoint, tables):
    """
    endpoint：传入的入端点 (link_id, timeslot)
    查询T表：T[src_link][dst_ts] = src_ts
    返回：(out_link, out_timeslot)
    查找失败返回 None
    """
    t_maps = tables.t_maps
    in_link = endpoint.link_id
    in_ts = endpoint.timeslot

    # 遍历这个link对应的T字典
    for out_ts, stored_src_ts in t_maps[in_link].items():
        if stored_src_ts == in_ts:
            # 查到了，再去S表找对应的输出link
            s_map = tables.s_map
            out_link = s_map.get((in_link, out_ts))
            if out_link is not None:
                return (out_link, out_ts)
    return None
