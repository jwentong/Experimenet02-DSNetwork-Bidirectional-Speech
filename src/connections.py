"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions

def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """
    建立双向话路 A <--> B
    src→dst方向：
        T[src.link][dst.ts] = src.ts
        S[(dst.link, dst.ts)] = src.link
    双向：A→B 与 B→A 两套映射
    校验：
        1) a,b完全相同抛ValueError；端点参数非法抛ValueError
        2) connection_id已存在 → return False
        3) 检测所有资源冲突：T输出时隙占用、s_map键占用、端点被占用
    全部通过才写入t_maps/s_map/pairs；否则tables原样不动返回False
    返回 True=成功，False=冲突/重复ID
    """
    a_link = endpoint_a.link_id
    a_ts = endpoint_a.timeslot
    b_link = endpoint_b.link_id
    b_ts = endpoint_b.timeslot

    # 非法端点：两端完全一样抛ValueError
    if (a_link == b_link) and (a_ts == b_ts):
        raise ValueError()
    # 端点合法性检查：链路只能0/1；时隙业务时隙：1~31且!=16
    def ep_check(ep):
        if ep.link_id not in (0,1):
            raise ValueError()
        if not (1 <= ep.timeslot <=31) or ep.timeslot ==16:
            raise ValueError()
    ep_check(endpoint_a)
    ep_check(endpoint_b)

    # 重复连接ID直接拒绝
    if connection_id in tables.pairs:
        return False

    # ========== 两个方向需要写入的表项 ==========
    # 方向1：A → B
    t1_key_outlink = a_link
    t1_out_ts = b_ts
    t1_in_ts = a_ts
    s1_key = (b_link, b_ts)
    s1_in_link = a_link

    # 方向2：B → A
    t2_key_outlink = b_link
    t2_out_ts = a_ts
    t2_in_ts = b_ts
    s2_key = (a_link, a_ts)
    s2_in_link = b_link

    # --------冲突检测（只检查，不写）--------
    # T输出时隙冲突：t_maps[out_link][out_ts] 是否已存在
    t_conflict = False
    # A→B的T：t_maps[a_link][b_ts] 是否已有
    if t1_out_ts in tables.t_maps[t1_key_outlink]:
        t_conflict = True
    # B→A的T：t_maps[b_link][a_ts] 是否已有
    if t2_out_ts in tables.t_maps[t2_key_outlink]:
        t_conflict = True

    # S表键冲突
    s_conflict = False
    if s1_key in tables.s_map:
        s_conflict = True
    if s2_key in tables.s_map:
        s_conflict = True

    if t_conflict or s_conflict:
        return False

    # 全部校验OK，原子写入
    tables.t_maps[t1_key_outlink][t1_out_ts] = t1_in_ts
    tables.t_maps[t2_key_outlink][t2_out_ts] = t2_in_ts

    tables.s_map[s1_key] = s1_in_link
    tables.s_map[s2_key] = s2_in_link

    tables.pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """
    根据connection_id释放双向连接：
        删除双向T映射，删除双向S映射，删除pairs记录
    不存在该id返回False；成功释放返回True
    """
    if connection_id not in tables.pairs:
        return False
    ep_a, ep_b = tables.pairs[connection_id]
    a_link = ep_a.link_id
    a_ts = ep_a.timeslot
    b_link = ep_b.link_id
    b_ts = ep_b.timeslot

    # 删除A→B T表项 t_maps[a_link][b_ts]
    if b_ts in tables.t_maps[a_link]:
        del tables.t_maps[a_link][b_ts]
    # 删除B→A T表项 t_maps[b_link][a_ts]
    if a_ts in tables.t_maps[b_link]:
        del tables.t_maps[b_link][a_ts]

    # 删除S表两个key
    key_s1 = (b_link, b_ts)
    key_s2 = (a_link, a_ts)
    if key_s1 in tables.s_map:
        del tables.s_map[key_s1]
    if key_s2 in tables.s_map:
        del tables.s_map[key_s2]

    # 删除pairs记录
    del tables.pairs[connection_id]
    return True
