# AI协作记录

## 需求
使用AI辅助完成实验二的四个核心函数实现，仅允许修改src下的t_switch.py、s_switch.py、connections.py，以及学生自拟测试、报告和AI日志文件，不修改教师提供的测试和评分文件。

## 建议与采纳
AI提示先对照model_contract里的输出→输入映射方向检查，避免把T表方向写反。采纳该建议，先手动核对C1的双向控制表项，确认输出时隙对应输入时隙的方向后再写代码。双向连接采用先全部检查再统一写入的原子提交方式，避免写一半失败导致控制表不一致，该设计符合实验要求的失败时tables完全不变的约束。

## 验证证据
手算验证单T交换：输入TS1=11、TS3=33，控制表{1:3,3:1}，预期输出TS1=33、TS3=11。依次运行pytest test_t.py 6项全过、test_s.py 5项全过、test_connect.py 8项全过、test_disconnect.py 5项全过、test_integration.py 5项全过，合计29项教师测试全部通过。运行run_experiment生成的16条传送记录零错配，一帧延迟验证正确。本地run_grading.py结果功能分项全部满分。
