# 实验二报告

姓名：吕林敏  
学号：2024280019  
GitHub：nickyhappy86-dotcom

## 原理与手算

T 接线器在同一链路内改变时隙，控制表采用“输出时隙 → 输入时隙”的方向；S 接线器在同一时隙位置选择输入链路，只改变链路号，不改变时隙号。两种单元都先把未连接的业务位置填为 `IDLE=0xD5`，并把 TS0、TS16 从本链路原位置透传。固定路径为先 T 后 S，输入帧 k 的结果在输出帧 k+1 可用，因此基础模型有一帧缓存延迟。

T 的手算例子：输入 TS1=11、TS3=33，控制表 `{1:3, 3:1}`。因为输出 TS1 取输入 TS3，所以输出 TS1=33；输出 TS3 取输入 TS1，所以输出 TS3=11。

S 的手算例子：在 TS3 将输出链路 0 选择输入链路 1，即 `s_map[(0,3)]=1`，结果为 `out[0,3]=input[1,3]`，时隙仍然是 TS3。

C1 连接 A=(0,1)、B=(1,5)：

- A→B：`T0[5]=1`，`S[(1,5)]=0`
- B→A：`T1[1]=5`，`S[(0,1)]=1`

`sample_frame(0)` 中 A 的字节为 3，B 的字节为 116。输入帧 0 经交换后应在输出帧 1 的 B 位置得到 3，在 A 位置得到 116。四帧、两对连接、两个方向合计 16 次校验。

## 结果分析

运行 `src.run_experiment` 后生成 `results/transfer_check.json`、`results/control_tables.json` 和 `results/switch_mapping.png`。16 条传送记录全部满足预期，`mismatches=0`，`latency_frames=1`，`conflict_rejected=true`，`release_ok=true`，`survivor_ok=true`。

C1 和 C2 可以同时存在：C1 使用 A=(0,1)、B=(1,5)，C2 使用 C=(0,2)、D=(1,6)。两对连接的四个方向都逐字节正确。尝试建立与 C1 内部 T 资源冲突的连接时，函数返回 `False`，原控制表完全不变，C1 仍能正常传送。释放 C1 后，C1 的两组 T/S 表项被删除，C2 的表项保持不变；释放出的资源可以重新建立新连接。

`control_tables.json` 的 `before_release` 中可以看到两条连接的四组 T/S 表项；`after_release` 只保留 C2 的 `T0[6]=2`、`T1[2]=6`、`S[(1,6)]=0`、`S[(0,2)]=1`。这说明释放操作只影响指定连接。

## 反例与验证

自拟测试 `student_tests/test_my_case.py` 包含两个测试。第一个测试先建立 C1，再请求端点未被占用但需要 `T0[5]` 的 C2，验证内部 T 阻塞会原子拒绝；释放 C1 后再建立 C2，验证资源可重用。第二个测试验证 S 交换保持时隙号、只改变链路，并检查未连接位置为 `IDLE`、TS0/16 原样透传、输入数组未被修改。

实际运行：

```text
31 passed（环境、T、S、连接、释放、集成）
2 passed（学生自拟测试）
```

公开测试和自拟测试均通过，教师测试与评分文件未修改。

## 局限

本实验采用固定的先 T 后 S 单路径，因此可能出现内部 T 输出阻塞，但不实现自动绕路或多级路径搜索。一帧缓存是课堂约定，不代表所有真实 T 接线器的物理延迟。TS16 保留也是本课程配置，不代表所有 E1 配置。实验未实现真实呼叫控制、信令编码、音频播放或操作系统实时调度；后续实验才把控制表接入呼叫状态机。

## 参考资料

1. 《实验二_PRD_数字交换网络与双向话路配置.docx》，V1.0，2026-11-09。
2. 课程仓库 `README.md` 与 `docs/model_contract.md`。
3. `src/models.py`、`src/engine.py` 与四个任务函数的 docstring。
4. `grading/test_t.py`、`test_s.py`、`test_connect.py`、`test_disconnect.py`、`test_integration.py`。
