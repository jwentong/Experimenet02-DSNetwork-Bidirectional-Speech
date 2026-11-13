# 实验二报告：数字交换网络与双向话路配置
姓名：罗成
学号：2024280195

## 原理与手算

T 接线器改变时隙，按输出时隙查找输入时隙；S 接线器改变链路，在相同的时隙位置选择输入链路。对方向 src→dst，控制表写作 T[src.link_id][dst.timeslot]=src.timeslot，以及 S[(dst.link_id,dst.timeslot)]=src.link_id。以 A=(0,1)、B=(1,5) 为例，A→B 写入 T0[5]=1、S[(1,5)]=0；B→A 写入 T1[1]=5、S[(0,1)]=1。帧0中 A 的样本值为3、B的样本值为116，因此输出帧1的 B 位置应为3、A位置应为116。T与S组合总延迟为一帧。

## 结果分析

环境自检和核心/集成测试共31项全部通过。运行 `python -m src.run_experiment` 后，`results/transfer_check.json` 记录了两组连接、四帧及两个方向共16次传送校验，实际值均与预期值一致，mismatches为0，available_frame_id比input_frame_id大1。结果还记录了冲突请求被拒绝、C1释放成功且C2继续传送。`results/control_tables.json` 显示释放前两组连接均在表中，释放后只剩C2；仿真同时生成了 `results/switch_mapping.png`。

## 反例与验证

自拟测试使用形状为(2,32)的uint8数组作为T单元输入，违反T接口要求的一维32时隙帧。预期 `t_switch` 抛出ValueError，且不得改动原输入。测试在 `student_tests/test_my_case.py` 中实际调用函数并比较调用前后的数组。执行 `python -m pytest student_tests -q`，结果为1 passed。项目核心测试使用 `python -m pytest grading/test_environment.py grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py -q`，结果为31 passed。

## 局限

本实验固定使用先T后S的路径，内部T输出冲突时直接拒绝，不进行多级网络寻路。整帧缓存和一帧延迟是本仿真的教学约定，不等于所有真实T接线器的物理延迟；程序也不实现真实E1帧同步、信令、呼叫状态机或实时调度。TS0和TS16在本模型中保留并原位透传，TS16保留规则不代表所有E1配置。