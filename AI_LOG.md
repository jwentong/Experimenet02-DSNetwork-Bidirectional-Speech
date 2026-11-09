# AI协作记录

## 需求

本次实验在完成手动推演控制表的基础上，使用AI辅助核对Python数组类型约束与边界异常处理。实验要求仅修改 `src/t_switch.py`、`src/s_switch.py`、`src/connections.py` 三个源码文件以及 `student_tests/test_my_case.py`、`REPORT.md`、`AI_LOG.md`，严格保持教师提供的函数接口不变。

## 建议与采纳

1. **我方判断与需求输入**：手算明确了“输出指向输入”的控制表规则以及双向连接 `src -> dst` 写入 `T[src.link_id][dst.timeslot] = src.timeslot` 和 `S[(dst.link_id, dst.timeslot)] = src.link_id` 的映射关系，要求检查双向原子性。
2. **AI建议与采纳理由**：在 `connect_pair` 中，AI建议将“两阶段提交（先遍历两个方向检查 `t_maps` 键值与 `s_map` 键冲突，全部通过后再统一写入字典）”拆分为独立循环，防止一个方向通过而反方向冲突时污染 `tables`；在 `t_switch` 和 `s_switch` 中，先完成全部键值的整数类型、范围及 `RESERVED`（TS0/16）校验，再新建 `np.uint8` 数组填充 `IDLE` 并透传保留时隙。经核对符合模型契约，予以采纳。

## 验证证据

1. **手算预期**：对于 `C1: (0,1)<->(1,5)`，帧0的 `A(0,1)=3`、`B(1,5)=116` 应在帧1互换位置输出；当存在 `C1` 时再请求 `(0,2)<->(0,5)` 会因争夺 `T0[5]` 触发内部阻塞返回 `False`。
2. **实际运行命令**：依次执行了 `.\.venv\Scripts\python.exe -m pytest grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py -q`、`.\.venv\Scripts\python.exe -m src.run_experiment`、`.\.venv\Scripts\python.exe -m pytest student_tests -q` 以及 `.\.venv\Scripts\python.exe grading/run_grading.py --local`。
3. **测试结果**：31项公开核心与集成测试、自拟内部阻塞测试全部通过，`results/` 下成功生成16条零错配传送记录与控制表快照，本地自动评分达到满分100分。
