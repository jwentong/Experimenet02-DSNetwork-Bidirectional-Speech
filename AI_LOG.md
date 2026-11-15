# AI协作记录

## 需求

工具：DeepSeek Harness 编码助手（deepseek-flash），Python 3.12，pytest 9。

任务：按教师仓库的 `docs/model_contract.md` 与 PRD 完成实验二的四个函数——`t_switch`、`s_switch`、`connect_pair`、`disconnect_pair`，不改教师测试、评分脚本与接口，并生成 `results/` 下的两个 JSON 与一张 PNG。

允许修改的文件：`src/t_switch.py`、`src/s_switch.py`、`src/connections.py`、`student_tests/test_my_case.py`、`REPORT.md`、`AI_LOG.md`。

## 建议与采纳

**建议一：先查完两个方向再写表。** 双向连接是两个方向共用一对端口，若先写 A→B 再检查 B→A 失败，控制表就会留下半条连接。AI 建议把校验拆成“端口合法性 → ID 重复 → 端点占用 → T 输出键 → S 输出键”五步，全部通过后统一提交。采纳：`connect_pair` 里两次循环，第一次只检查，第二次才写 `t_maps`、`s_map` 和 `pairs`。

**建议二：T 与 S 的冲突要按“链路 + 时隙”判重，不能只按时隙号。** 端点用 `(link_id, timeslot)` 标识，T 表按输入链路分开存 `{输出时隙: 输入时隙}`，S 表按 `(输出链路, 时隙)` 存输入链路。采纳并写成自拟测试：同一个时隙号 5 在链路 0 的 T 表被占用时拒绝，但换到链路 1 的 T 表就应允许。

**建议三：释放只按 `pairs[id]` 回删。** 释放时用 `directions(a, b)` 重新推出两组键并 `pop`，再删除 `pairs[id]`，这样既不会漏删 S 表，也不会误删其他连接。采纳，并在自拟测试中用“释放后同端口重建”验证。

**边界验证而非纠错**：本次四个函数首次实现即通过 39 项公开测试，没有出现需要返工的错误；因此按 PRD “首次正确也要记录边界验证”的要求，把验证重点放在两个边界上——同号时隙跨链路不算冲突、释放后资源可重用。

## 验证证据

**手算预期**：C1 为 A=(0,1)、B=(1,5)，应有 T0[5]=1、S[(1,5)]=0、T1[1]=5、S[(0,1)]=1；`sample_frame(0)` 中 A 的字节是 3、B 的字节是 116，输出帧 1 应在 B 位置读到 3、A 位置读到 116。

**实际运行的命令与结果**：

```
python -m src.run_experiment
16 direction/frame checks passed; conflict rejected; release and surviving pair verified.
mismatches = 0，latency_frames = 1，conflict_rejected/release_ok/survivor_ok 均为 True

python -m pytest grading -q
44 passed

python -m pytest student_tests -q
2 passed

python grading/run_grading.py --local
实验 70/70，报告 30/30，总分 100/100
```

**边界证据**：`test_same_slot_different_link_is_not_a_conflict` 断言 `t_maps[0][5]` 仍为 1、`t_maps[1][5]` 为 2、`s_map[(0,5)]` 为 1，并实际交换一帧确认两条连接同时传送；`test_release_frees_port_for_reuse` 断言释放后两个方向都读到 `IDLE`，重建后字节恢复。两项均通过。
