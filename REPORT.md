# 实验二 数字交换网络与双向话路配置

姓名：杨欣  
学号：2025280305

## 原理与手算

本实验在两条输入、两条输出链路上实现固定先T后S的数字交换，每条链路一帧有32个uint8样本。帧率为8000帧/s，帧周期为125 μs，每链路速率为32×8×8000=2.048 Mbit/s，每个时隙通道为64 kbit/s。TS0和TS16按本链路原位透传，其余30个时隙用于业务。未连接的业务输出填0xD5，但0xD5也可能是有效业务字节，因此必须按控制表判断资源占用。

T接线器改变时隙，控制表为“输出时隙→输入时隙”。例如输入TS1=11、TS3=33，配置{1:3,3:1}，得到输出TS1=33、TS3=11。输出为独立数组，输入保持不变。S接线器改变链路而不改变时隙：配置S[(0,3)]=1后，输出链路0的TS3取自输入链路1的TS3，不能取TS1或TS5。对于sample_frame(0)，链路1的TS3为101+3×3=110，因此该S输出为110。

C1连接A=(0,1)与B=(1,5)，C2连接C=(0,2)与D=(1,6)。控制表如下。

|方向|T控制表|S控制表|
|---|---|---|
|A→B|T0[5]=1|S[(1,5)]=0|
|B→A|T1[1]=5|S[(0,1)]=1|
|C→D|T0[6]=2|S[(1,6)]=0|
|D→C|T1[2]=6|S[(0,2)]=1|

样本公式为(link×101+slot×3+k×17) mod 256。输入帧0的A、B、C、D分别为3、116、6、119，所以输出帧1的B、A、D、C分别应为3、116、6、119。T和S组合的结果只增加一帧可用延迟，由engine统一标记available_frame_id=k+1，S不能再叠加一帧。

## 结果分析

本次使用补全后的实现运行教师入口python -m src.run_experiment，实际生成results/transfer_check.json、results/control_tables.json和results/switch_mapping.png。四帧、两对连接、每对两个方向共16条记录，所有expected均等于actual，mismatches=0，latency_frames=1，每条available_frame_id均等于input_frame_id+1。以下为JSON中的实际接收字节。

|输入帧k|输出可用帧|A→B|B→A|C→D|D→C|
|---|---|---|---|---|---|
|0|1|3|116|6|119|
|1|2|20|133|23|136|
|2|3|37|150|40|153|
|3|4|54|167|57|170|

control_tables.json中释放前T表为[{5:1,6:2},{1:5,2:6}]，S表包含四条方向的输出选择。释放C1后T表为[{6:2},{2:6}]，S表仅保留S[(1,6)]=0和S[(0,2)]=1，pairs中仅有C2。transfer_check.json的conflict_rejected、release_ok和survivor_ok均为true，分别表示已占端点连接请求被整体拒绝、C1两端输出恢复0xD5、C2仍双向逐字节正确。

switch_mapping.png绘制输入帧0两条链路的样本，以及输出帧1上四个已连接位置的字节。链路0的输出TS1、TS2为116、119，链路1的输出TS5、TS6为3、6，与手算一致。该图用于展示连接输出，不代替JSON中的16条逐字节验证。

## 反例与验证

自拟测试位于student_tests/test_my_case.py，输入及预期在此先列出。

1. 内部T阻塞与释放重用：先建立C1和C2，再请求(0,3)与(0,5)。这两个新端点均未占用，但新路径需要C1已占用的T0[5]，应返回False且整个Tables与深拷贝快照相等。随后验证原C1仍双向传送；释放C1后两个端点输出为空闲且C2双向保持正确；再次请求同一组被阻塞端点应成功，两个方向均逐字节正确。这组用例验证端点空闲不代表内部路径可用。
2. 反向S冲突的原子性：预置S[(0,4)]=0，再请求(0,4)与(1,8)。虽然正方向资源空闲，反方向的S输出已占用，所以应整体拒绝，不能写入正方向T/S表项，Tables应完全不变。
3. 不同链路相同时隙及空闲码：同时建立链路0的TS7↔TS8和链路1的TS7↔TS8，两对连接应共存。把输入[0,7]设为0xD5，输出[0,8]应仍正确传送该值；再次占用(0,7)应被拒绝。释放链路0连接后，链路1连接的两个方向应保持正确，证明端点必须由链路号和时隙号联合识别。

这些测试均直接调用实验函数并使用assert检查控制表或字节，不以文件存在或界面状态代替数据传送验证。教师测试和评分文件保持原样。

实际在项目根目录执行以下命令：

```powershell
.\.venv\Scripts\python.exe -m src.test_environment
.\.venv\Scripts\python.exe -m pytest grading/test_environment.py grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py student_tests -q
.\.venv\Scripts\python.exe -m src.run_experiment
```

环境自检输出Environment OK；上述pytest执行结果为34 passed，包括31项教师环境、核心和集成用例以及3项自拟测试。仿真入口输出16 direction/frame checks passed，并确认冲突拒绝、连接释放及保留连接正常。

随后执行.\.venv\Scripts\python.exe grading/run_grading.py --local，本地公开规则评分为100/100：环境5/5、T交换20/20、S交换15/15、双向连接20/20、释放15/15、整体验证10/10、自拟测试5/5、产物与文档10/10。该次评分共37项顶层检查通过，其中自拟测试检查会另行调用三个自拟测试。评分原始记录保存在.grade/grade_report.json和.grade/grade_result.txt，交付包中同时保存在verification目录。这是本地预览成绩，课程成绩以教师仓库云端对实际提交的评分为准。

## 局限

本实验固定采用T→S路径，存在内部阻塞，不执行自动绕路或多级交换路径搜索。控制表变化发生在两次帧处理之间，不模拟并发修改。整帧缓存和一帧可用延迟属于本实验模型，不能推广为所有真实T接线器的物理时延；Python离线仿真也不代表操作系统能够每125 μs实时唤醒。

模型只验证8 bit字节的数据面传送，尚未实现用户摘挂机、呼叫状态机、真实音频、SIP、信令编码或真实E1帧同步。TS16保留是本课程配置，不能视为所有E1配置的通用要求；实验一的128 bit/tick服务模型也不能直接当作本次PCM链路速率。后续呼叫控制可以复用Endpoint、Tables及连接和释放接口。
