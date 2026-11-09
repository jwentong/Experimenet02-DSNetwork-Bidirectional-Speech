# AI协作记录

## 需求

使用环境内置的AI编程助手（WorkBuddy）协助完成实验二。要求与允许修改范围：只补全src/t_switch.py、src/s_switch.py、src/connections.py的四个函数，另写student_tests/test_my_case.py、REPORT.md与AI_LOG.md；src/models.py、src/engine.py、src/run_experiment.py与grading/下的教师测试一律不改动，接口与函数签名保持原样。提示中明确给出三个约束：控制表方向为输出指向输入；路径固定先T后S；双向连接必须两端全部检查通过后原子写入，且时延为一帧。执行环境另有一处限制需要说明：校园网代理拦截了git与curl，教师仓库无法clone，因此src与grading中的教师文件是按公开仓库逐文件取回后原样落地的，未改动其逻辑。

## 建议与采纳

AI先通读PRD与docs/model_contract.md，再一个一个函数补全，这一点采纳：先写t_switch，跑grading/test_t.py；再写s_switch，跑test_s.py；最后写connections，跑test_connect.py与test_disconnect.py，避免四个函数同时出错时难以定位。

AI建议"先整体校验映射再生成输出数组"，采纳并实现为两段式：t_switch与s_switch都先把控制表全部校验完，再np.full填IDLE、复制保留时隙、写入映射，这样非法表项不会产生半成品结果；connect_pair同样采用"阶段一只记录计划、阶段二统一提交"，以满足拒绝时tables完全不变的要求。

AI第一版connect_pair在检查两个方向互相冲突时，把内部T输出键与S输出键放进同一个集合去重，结果在test_same_timeslot_other_links上失败：A=(0,7)与B=(1,7)时，正向的T键(0,7)与反向的S键(0,7)被误判为同一资源。判断后修正为两个独立集合t_keys与s_keys，因为T输出与S输出属于不同资源空间，键相同也不能互相顶替；修正后该用例通过。

AI还建议按模型约定把"字节值等于IDLE"与"端口空闲"彻底分开：占用判断只查pairs中的端点与两张控制表的键，从不比较字节内容，因此输入某时隙恰好为0xD5时仍视为占用，这一点与test_idle_byte_is_not_free_resource的预期一致。

## 验证证据

手算预期先于实现写出：C1的A=(0,1)、B=(1,5)应为T0[5]=1、S[(1,5)]=0与T1[1]=5、S[(0,1)]=1；sample_frame(0)中A为3、B为116，故输出帧1应在(1,5)得到3、在(0,1)得到116。

实际命令与结果：.\.venv\Scripts\python.exe -m src.test_environment输出"Environment OK: NumPy, Matplotlib, pytest; 2 links x 32 slots."；分项运行test_t.py得6 passed、test_s.py得5 passed、test_connect.py得8 passed、test_disconnect.py得5 passed、test_integration.py得5 passed，合计31项全部通过。

运行.\.venv\Scripts\python.exe -m src.run_experiment输出"16 direction/frame checks passed; conflict rejected; release and surviving pair verified."，results/transfer_check.json中mismatches=0、latency_frames=1；results/control_tables.json释放前t_maps为[{"5":1,"6":2},{"1":5,"2":6}]，释放C1后为[{"6":2},{"2":6}]，与预期一致。

自拟测试运行.\.venv\Scripts\python.exe -m pytest student_tests -q，输出"1 passed"，覆盖三条连接共存、部分释放、T0[5]回收后重建C5以及重复释放返回False。
