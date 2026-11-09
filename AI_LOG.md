# AI协作记录

## 需求

使用 OpenAI Codex 辅助完成实验二的四个函数：`t_switch`、`s_switch`、`connect_pair`、`disconnect_pair`。只修改任务源码、报告、AI 记录和自拟测试，不修改教师测试、评分脚本或框架接口。先手算控制表，再逐项实现和验证。

## 建议与采纳

AI 建议 T 交换严格按“输出时隙 → 输入时隙”查表，TS0/16 原位透传；S 交换只改变链路，保持时隙号；双向连接必须先检查两个方向的端点、内部 T 输出和 S 输出资源，全部通过后再一次性写表，避免冲突时留下半成品；释放时按 `pairs` 找到两端，删除两组 T/S 表项，不能影响其他连接。以上建议已采纳，并用公开测试和自拟反例验证。

实现过程中遇到一个环境问题：D 盘嵌入式 Python 的 `_pth` 不包含当前项目目录，直接运行 pytest 时出现 `ModuleNotFoundError: src`。解决方式是在调用 pytest 前用 Python 将项目根目录插入 `sys.path`，没有修改教师测试或项目接口。

## 验证证据

- 手算：C1 为 `T0[5]=1, S[(1,5)]=0`；反向为 `T1[1]=5, S[(0,1)]=1`。
- 自拟测试 1：C1 存在时请求需要 `T0[5]` 的 C2，验证返回 `False` 且控制表完全不变；释放 C1 后 C2 可建立。
- 自拟测试 2：S 交换保持时隙号，未连接位置为 `IDLE`，TS0/16 原样透传，输入数组不变。
- 实际运行 `31 passed`（环境、T、S、连接、释放、集成）和 `2 passed`（自拟测试）。
- `results/transfer_check.json`：16 条校验、`mismatches=0`、`latency_frames=1`、冲突拒绝、释放和保留连接均通过。
- `results/control_tables.json` 和 `results/switch_mapping.png` 已由本人的实现和仿真入口实际生成。
