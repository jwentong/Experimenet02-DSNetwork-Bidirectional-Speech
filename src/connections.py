"""任务三与四：双向连接控制与释放。"""
from src.models import validate_endpoint, directions


def connect_pair(connection_id, endpoint_a, endpoint_b, tables):
    """原地建立双向T→S映射，成功返回True。
    非法端口或两端相同抛ValueError。ID已存在、端口已占用、
    内部T输出或S输出资源冲突，返回False且tables完全不变。
    方向src→dst: T[src.link_id][dst.timeslot]=src.timeslot;
    S[(dst.link_id,dst.timeslot)]=src.link_id。
    两个方向全部检查通过才写表，并记录pairs[id]=(a,b)。
    本实验固定路径可能发生内部阻塞，不要求自动改走其他路径。
    """
    t_maps = tables.t_maps
    s_map = tables.s_map
    pairs = tables.pairs

    validate_endpoint(endpoint_a)
    validate_endpoint(endpoint_b)

    if endpoint_a.link_id == endpoint_b.link_id and endpoint_a.timeslot == endpoint_b.timeslot:
        raise ValueError("两端端点相同")

    if connection_id in pairs:
        return False

    # 方向1：a -> b
    src1 = endpoint_a
    dst1 = endpoint_b
    # 方向2：b -> a
    src2 = endpoint_b
    dst2 = endpoint_a

    # -------- 预校验：严格按 src→dst 公式检查冲突 --------
    # T冲突：T[src.link][dst.ts] 是否已经存在key
    t_conf1 = dst1.timeslot in t_maps[src1.link_id]
    t_conf2 = dst2.timeslot in t_maps[src2.link_id]
    # S冲突：S[(dst.link, dst.ts)] 是否存在
    s_conf1 = (dst1.link_id, dst1.timeslot) in s_map
    s_conf2 = (dst2.link_id, dst2.timeslot) in s_map

    if t_conf1 or t_conf2 or s_conf1 or s_conf2:
        return False

    # -------- 写入，严格按注释公式 --------
    # src1 -> dst1
    t_maps[src1.link_id][dst1.timeslot] = src1.timeslot
    s_map[(dst1.link_id, dst1.timeslot)] = src1.link_id
    # src2 -> dst2
    t_maps[src2.link_id][dst2.timeslot] = src2.timeslot
    s_map[(dst2.link_id, dst2.timeslot)] = src2.link_id

    pairs[connection_id] = (endpoint_a, endpoint_b)
    return True


def disconnect_pair(connection_id, tables):
    """释放指定ID的两个方向及pairs记录，成功返回True。
    不存在或重复释放返回False，不能影响其他连接。
    输出回到IDLE由未连接映射的T/S发送规则自然产生。
    """
    t_maps = tables.t_maps
    s_map = tables.s_map
    pairs = tables.pairs

    if connection_id not in pairs:
        return False

    ep_a, ep_b = pairs.pop(connection_id)
    # a->b
    src1 = ep_a
    dst1 = ep_b
    # b->a
    src2 = ep_b
    dst2 = ep_a

    del t_maps[src1.link_id][dst1.timeslot]
    del s_map[(dst1.link_id, dst1.timeslot)]
    del t_maps[src2.link_id][dst2.timeslot]
    del s_map[(dst2.link_id, dst2.timeslot)]

    return True
