# AI协作记录

## 需求

在本次实验中，我使用了AI工具（大语言模型）辅助我理解现代交换原理中的T/S接线器模型，并帮助我完成代码编写与排错。本次AI协作仅允许修改教师指定的 `src/t_switch.py`、`src/s_switch.py` 和 `src/connections.py` 三个代码文件，以及协助撰写本报告。未要求AI修改任何教师测试或评分脚本。

## 建议与采纳

1. AI建议T接线器创建全填 `IDLE` 的新数组，并特别提醒TS0/16需要从原输入透传，且如果映射表包含保留时隙需抛出 `ValueError`。我阅读 `models.py` 后确认了常量定义，采纳了该建议。
2. 对于 `connect_pair`，AI建议先遍历两个方向检查 T 表和 S 表是否冲突，包括内部输出冲突和端点占用，只有全部通过才写入，否则返回 `False` 且保持原表不变。我手算 C1、C2 控制表后认为逻辑严密，予以采纳。
3. 在 PowerShell 中因路径嵌套和虚拟环境激活导致 `pytest` 找不到文件，AI指出应直接使用 `python -m pytest` 命令，修正了运行方式。

## 验证证据

- 手算预期：C1 双向连接 (0,1) 与 (1,5) 时，T0[5]=1，S[(1,5)]=0；T1[1]=5，S[(0,1)]=1。输入帧 0 的字节在输出帧 1 生效。
- 实际运行命令与结果：
  - `python -m pytest grading/test_t.py -q` -> `6 passed`
  - `python -m pytest grading/test_s.py -q` -> `5 passed`
  - `python -m pytest grading/test_connect.py -q` -> `8 passed`
  - `python -m pytest grading/test_disconnect.py -q` -> `5 passed`
  - `python -m pytest grading/test_integration.py -q` -> `5 passed`
  - `python -m src.run_experiment` -> 成功生成 3 个产物文件，验证 16 次数据传送、零错配及一帧延迟。
  - `python -m pytest student_tests -q` -> `1 passed` (自拟测试)。
- 边界验证：在自拟测试中，额外验证了未连接时隙是否被正确填充为 `IDLE`（0xD5）。