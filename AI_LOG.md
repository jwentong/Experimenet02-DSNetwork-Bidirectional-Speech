# AI协作记录

## 需求
使用Claude Code辅助实现实验二四个函数。需求：补全t_switch、s_switch、connect_pair、disconnect_pair，不改教师接口与测试，并生成报告、自拟测试与成果文件。

## 建议与采纳
AI先阅读docs/model_contract.md与各测试，指出控制方向为“输出→输入”、固定先T后S、双向连接需先检查两个方向再原子写表。采纳其“先检查后写入、失败不改动表”的实现，并补充显式端点占用检查与保留时隙透传。

## 验证证据
手算C1双向控制表后运行pytest，grading下T/S/连接/释放/集成共29项测试全部通过；运行python -m src.run_experiment输出16次校验全部匹配、冲突拒绝、释放后保留连接正常；自拟反例与重用例测试通过。
