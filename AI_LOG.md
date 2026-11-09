# AI协作记录

## 需求

本次使用Codex辅助完成实验二数字交换网络与双向话路配置。提供的资料是实验规范DOCX；Codex读取其中的交付要求，获取教师仓库，并检查docs/model_contract.md、四个目标函数的docstring、教师帧推进框架和公开测试。按要求只补全src/t_switch.py、src/s_switch.py和src/connections.py中的四个函数，另编写报告、自拟测试和结果文件，不修改教师模型、引擎、仿真入口或评分测试。姓名和学号由本人在对话中提供。

## 建议与采纳

实现采用“输出→输入”的查表方向：T先在源链路上把样本放到目的时隙，S再在相同时隙选择源链路。连接管理采用两阶段处理，先验证两个端点、ID、端点占用和两个方向的T/S资源，全部通过才一次写入表项及pairs。拒绝连接时不回滚部分写表，而是保证预检期间没有写操作。释放按pairs恢复两个方向的资源键，只清除该连接。

采纳上述方案是因为它直接对应课程的固定T→S路径和双向原子建立约定。IDLE仅用于空闲输出填充，端点是否空闲由pairs与控制表判断。保留时隙在T和S各自原位透传；一帧延迟由教师engine统一标记，不在两个交换函数中重复添加。自拟测试进一步验证反方向S资源冲突不会留下正方向映射，以及不同链路上相同时隙号不能被误判为同一个端点。初次依赖下载受到网络权限和下载通道限制，获得联网权限后改用清华PyPI镜像安装；没有为绕过测试删改评分文件。

## 验证证据

编码前先按规范手算：T映射{1:3,3:1}将11和33交换；C1的正向表项为T0[5]=1与S[(1,5)]=0，反向为T1[1]=5与S[(0,1)]=1。sample_frame(0)中A=3、B=116，预期输出帧1的B=3、A=116。

实际运行python -m src.test_environment，输出Environment OK；随后执行python -m pytest grading/test_environment.py grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py student_tests -q，结果34 passed。再执行python -m src.run_experiment，输出16 direction/frame checks passed，冲突被拒绝、释放和保留连接验证成功。以上命令均使用项目.venv中的Python解释器。results中的两个JSON及PNG由本次实现实际生成，没有复制教师示例结果。

读取transfer_check.json核对16条expected与actual一致、mismatches=0、latency_frames=1，三个布尔验证标志均为true；读取control_tables.json确认释放后只剩C2的表项。自拟测试的三个函数全部通过，覆盖内部T阻塞后资源重用、反方向S冲突的整表不变性、不同链路同号端点和有效空闲码字节。没有发生需要编造的AI错误或人工测量过程。

最后实际执行.\.venv\Scripts\python.exe grading/run_grading.py --local，结果100.0/100，八个评分分组均为completed，37项顶层检查全部通过。原始JSON、文字成绩和各组日志保留在交付包verification目录。检查交换图可正常打开且标记与手算字节一致；git diff确认教师原有受版本控制的文件只修改了三个指定任务文件。该结果为本地验证，没有声称已创建个人Fork、向教师提交PR或获得云端最终成绩。
