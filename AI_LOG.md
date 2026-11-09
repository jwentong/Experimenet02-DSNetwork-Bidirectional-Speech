# AI协作记录

## 需求
本次实验使用ChatGPT辅助理解数字交换网络的实验要求、T/S交换原理、双向话路建立与释放机制，并协助分析程序实现和测试结果。

根据教师提供的实验规范，需完成src/t_switch.py、src/s_switch.py和src/connections.py中的4个核心函数，保留原有函数接口，不修改教师提供的models.py、engine.py、测试文件及自动评分程序。此外，还需完成student_tests/test_my_case.py自拟测试，以及REPORT.md、AI_LOG.md等实验文档。

实验过程中采用逐项实现、逐项测试的方式，每完成一个函数后运行对应的pytest测试，确认通过后再进入下一任务。

## 建议与采纳
1. T交换实现

AI建议采用“输出时隙→输入时隙”的控制表映射方式，先验证控制表是否合法，再创建新的输出数组，将未连接业务时隙初始化为IDLE，保留TS0和TS16原位透传，最后根据控制表完成时隙重排。

结合教师提供的函数注释检查了实现逻辑，确认其符合T交换只改变时隙、不改变链路的要求。采用该实现方式，并保留原函数接口。

2. S交换实现

AI建议使用二维NumPy数组保存两条链路的输出数据，通过spatial_map中的“(输出链路,时隙)→输入链路”映射，在相同时隙选择指定输入链路的数据。

检查后采用该方法，同时保留非法链路、非法时隙和保留时隙映射的异常处理，保证不修改原输入数据。

3. 双向连接建立

AI建议先检查两个端点的合法性、连接ID是否重复、端点是否已占用，以及两个方向的内部T/S资源是否发生冲突。只有全部检查通过后，才统一写入两个方向的控制表并登记pairs记录。

结合实验要求，确认该方法能够避免连接建立失败时只写入单向映射的问题，因此采用先检查、后提交的实现方式，保证冲突时原控制表保持不变。

4. 连接释放

AI建议通过pairs记录找到指定连接的两个端点，利用directions函数分别删除两个方向对应的T/S映射，最后删除连接记录。对于不存在或重复释放的连接ID直接返回False。

检查后采用该方案，确保释放指定连接时不影响其他已建立的连接。

5. 自拟测试与实验结果分析

在完成教师测试后，AI建议设计两组双向连接共存、释放其中一组连接、检查另一组连接不受影响，以及释放资源重新使用的自拟测试。采用该测试方案，并使用assert验证连接状态和控制表内容。

实验结束后，结合实际生成的transfer_check.json、control_tables.json和switch_mapping.png，对双向字节传输、控制表变化、内部冲突及一帧延迟进行分析。

## 验证证据
1. 原理与手算验证

以C1连接A=(0,1)、B=(1,5)为例，按照教师规定的控制表方向，手算得到：

A→B：T0[5]=1，S[(1,5)]=0。

B→A：T1[1]=5，S[(0,1)]=1。

根据样本生成公式，输入帧0中A端点字节值为3，B端点字节值为116。预期输出帧1中，链路1的TS5得到3，链路0的TS1得到116。

实际实验记录与预期一致。

2. 教师测试验证

使用项目独立虚拟环境，依次执行以下命令：

.\.venv\Scripts\python.exe -m src.test_environment
.\.venv\Scripts\python.exe -m pytest grading/test_environment.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_t.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_s.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_connect.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_disconnect.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_integration.py -q

实际测试结果：

环境测试：2 passed

T交换测试：6 passed

S交换测试：5 passed

双向连接测试：8 passed

连接释放测试：5 passed

整体集成测试：5 passed

累计31项教师公开测试全部通过。各核心函数在首次提交对应测试时均通过，未出现需要修改教师测试文件的情况。

3. 整体仿真验证

执行：

.\.venv\Scripts\python.exe -m src.run_experiment

终端输出：

16 direction/frame checks passed; conflict rejected; release and surviving pair verified.

检查transfer_check.json，16次数据传输的expected与actual全部一致，mismatches=0，latency_frames=1。

检查control_tables.json，释放C1后，C1的双向T/S映射全部删除，C2的连接及控制表项保持不变。

检查switch_mapping.png，输出链路0在TS1、TS2的字节分别为116、119，输出链路1在TS5、TS6的字节分别为3、6，与手算及JSON记录一致。

4. 自拟测试验证

在student_tests/test_my_case.py中设计连接共存、指定释放、资源重用和重复释放的测试，使用assert检查函数返回值、pairs记录及T/S控制表内容。

执行：

.\.venv\Scripts\python.exe -m pytest student_tests -q

实际结果：

1 passed in 0.03s

自拟测试通过，进一步验证了双向话路建立与释放功能的正确性。