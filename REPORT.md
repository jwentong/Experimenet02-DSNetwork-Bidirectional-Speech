# 实验二报告
姓名：姚智烁
学号：2024280127

## 原理与手算
T交换在同一链路内按“输出时隙→输入时隙”重排字节，改变的是时隙；S交换在同一时隙位置选择输入链路，只改链路不改时隙。控制表统一写“输出→输入”：对方向src→dst，T[src.link_id][dst.timeslot]=src.timeslot，S[(dst.link_id,dst.timeslot)]=src.link_id。C1连接A=(0,1)、B=(1,5)，两个方向分别写入T0[5]=1、S[(1,5)]=0，以及T1[1]=5、S[(0,1)]=1。输入帧k的字节在输出帧k+1可用，即一帧延迟。手算：sample_frame(k)字节为(link×101+slot×3+k×17) mod 256，A位置(0,1)字节为3、B位置(1,5)字节为116，经交换后输出帧1的B位置得到3、A位置得到116。

## 结果分析
运行python -m src.run_experiment后生成results/transfer_check.json、control_tables.json与switch_mapping.png。transfer_check.json记录4帧×2对连接×2方向共16次校验，mismatches=0，latency_frames=1，conflict_rejected=True、release_ok=True、survivor_ok=True。control_tables.json的before_release中t_maps为[{"5":1,"6":2},{"1":5,"2":6}]，after_release仅剩C2的映射，说明释放C1只清除其自身表项、C2继续正常。switch_mapping.png由本人实现与仿真入口实际生成。

## 反例与验证
自拟测试验证内部T输出阻塞：C1占用A=(0,1)、B=(1,5)后，请求(0,2)与(0,5)。虽然新端点未被C1占用，但方向(0,2)→(0,5)同样需要T0的输出TS5，必须整体拒绝且原表保持不变。用deepcopy比较断言connect_pair返回False且t==old，pytest student_tests -q通过。另一条测试验证释放C1后同一端点资源可被C2重用并逐字节正确传送。

## 局限
本模型固定先T后S路径，端口空闲也可能因内部T输出冲突发生阻塞，不自动寻找替代路径；真实T接线器未必采用整帧缓存，一帧延迟是本实验约定而非所有设备的物理延迟；TS16保留也是本课程配置。当前仅建立和释放静态话路，尚未实现信令、呼叫状态机与多级路径搜索。
