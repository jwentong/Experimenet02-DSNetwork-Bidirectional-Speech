# AI协作记录

## 需求

使用 WorkBuddy 桌面客户端（会话可见模型标识 DeepSeek-V4.1-Flash）辅助本次实验。允许修改的文件只有 src/t_switch.py、src/s_switch.py、src/connections.py，以及新增 results 产物、REPORT.md、AI_LOG.md、student_tests/test_my_case.py。教师测试 grading/ 与 src/models.py、src/engine.py 一律不改，接口与帧模型沿用仓库 docs/model_contract.md 的约定。

## 建议与采纳

1）先读 docs/model_contract.md 与四个目标函数的 docstring，确认“输出→输入”的映射方向，再逐个函数补全，避免一次生成整份实现。采纳：按 T、S、连接、释放的顺序各写一版，每写完一个就跑对应的 grading 测试。

2）关于端点占用的判定，最初的想法是额外遍历 pairs 检查两端是否已被其他连接使用。重新读 test_connect.py 的断言后发现，s_map 的键恰好就是两个端点的（链路，时隙），建立连接时必然写入，因此只要检查每个方向的目的端口 S 键是否存在，同时也就判定了端点占用和内部 S 冲突。采纳修正版：不再重复遍历 pairs，直接以 t_maps[src.link_id] 的目的时隙和 s_map 的（dst.link_id,dst.timeslot）作为唯一的资源判定，两条检查都不通过才返回 False。这一点用 test_idle_byte_is_not_free_resource 反向确认：字节值等于 0xD5 不影响占用判定。

3）关于校验时机，AI 建议把非法时隙的检查放在构造输出数组之前，且整张控制表先校验再写值。采纳，t_switch 与 s_switch 都是先全量校验、后写输出，保证非法映射抛 ValueError 时不产生半成品结果，也不改动输入。

4）AI 建议在 t_switch 里增加输入帧形状检查（必须是长度 32 的 uint8）。教师测试没有覆盖这一条，但保留不会影响任何公开用例，且能让误用二维数组时及早报错，故采纳。

5）AI 建议直接改 grading 里的断言以适配自己的实现，被明确拒绝：评分文件属于教师资产，任何“改测试让结果变绿”的做法都使实验失去意义。

## 验证证据

（1）手算先行：C1 的 A=(0,1)、B=(1,5) 在帧 0 的字节分别为 3 与 116，预期输出帧 1 的 (1,5)=3、(0,1)=116；自拟用例中 k=3 时链路 0 的 TS4=63、链路 1 的 TS9=179，先在纸上算出这两个数再写断言。

（2）实际命令与结果：`./.venv/Scripts/python.exe -m pytest grading/test_t.py -q` 6 passed；test_s.py 5 passed；test_connect.py 8 passed；test_disconnect.py 5 passed；test_integration.py 5 passed；test_environment.py 2 passed；共 31 项全部通过。`./.venv/Scripts/python.exe -m src.run_experiment` 生成两个 JSON 与 PNG，transfer_check.json 的 16 条记录 mismatches=0、latency_frames=1，control_tables.json 释放前后的表项与手算的 C1/C2 表一致。

（3）边界核对：TS0/TS16 在 T 与 S 两侧都是原位透传；控制表出现 0、16、32、-1 或链路 2 时都抛 ValueError 且输入数组不变（用 np.array_equal 比较前后副本）；重复 ID、端点占用、内部 T 输出冲突三种拒绝路径都用 deepcopy 前后对比确认 tables 完全未变；释放后重新建立同一对端点成功，说明 T 与 S 表项都已清理干净。

（4）产物由本人实现生成：results 下的两个 JSON 与 switch_mapping.png 来自本地 .venv 中运行 src/run_experiment.py 的实际输出，不是复制 examples/teacher_results 的参考文件。
