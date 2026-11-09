# AI协作记录

## 需求
使用 AI 辅助完成实验二，只允许修改 src/t_switch.py、src/s_switch.py、src/connections.py、REPORT.md、AI_LOG.md 和 student_tests/test_my_case.py；不改动教师提供的 models、engine、run_experiment 和 grading 测试。要求明确输出→输入方向、先T后S路径、双向原子建立与一帧延迟。

## 建议与采纳
AI 建议逐个函数实现并逐项跑测试；采纳。T交换先校验映射时隙再写新数组，避免改动输入；S交换只替换链路、保留 TS0/16 原位透传；connect_pair 先完成两个方向的端点占用、T输出与S输出冲突检查，全部通过后再统一写表，从而保证拒绝时 tables 不变；disconnect_pair 依据 pairs 反向删除四个表项，重复释放返回 False。

## 验证证据

手算预期：C1 双向控制表 T0[5]=1、S[(1,5)]=0、T1[1]=5、S[(0,1)]=1；帧0 字节 A=3、B=116，输出帧1 应在对应位置互换。

运行结果：

| 命令 | 结果 |
|---|---|
| python -m pytest grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py -q | 29 passed |
| python -m src.run_experiment | 16 direction/frame checks passed，mismatches=0 |
| python -m pytest student_tests -q | 1 passed |
