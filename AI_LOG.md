# AI协作记录

## 需求

本次实验二中，我用AI作为实现与查错的辅助工具：先读docs/model_contract.md、函数docstring和教师测试，再让AI补全src/t_switch.py、src/s_switch.py、src/connections.py三个文件的四个函数。允许AI改动的只有这三个实现文件和REPORT.md、AI_LOG.md、student_tests/test_my_case.py；models.py、engine.py、run_experiment.py和grading/下的教师测试与评分脚本保持原样，没有修改。

## 建议与采纳

AI建议先把控制表整体校验完再生成输出帧，我采纳：t_switch和s_switch先检查映射中的链路、时隙是否为业务时隙，遇到TS0/TS16、负数或超范围时隙直接抛ValueError，再构造新数组，这样输入帧不会被原地修改。AI还建议connect_pair先检查两个方向再统一写表，我采纳并补充了内部T输出和S输出的占用检查（即使映射值相同也不共享表项），使拒绝时tables完全不变；disconnect_pair用带默认值的pop按pairs记录删除，避免重复释放抛异常。AI提出过用整表深拷贝做回滚，我认为本实现先检查后写入，不需要中间回滚，最终采用检查通过后一次性写表的方式。

## 验证证据

手算证据：sample_frame(0)中A=(0,1)的字节为3、B=(1,5)的字节为116，控制表T0[5]=1、S[(1,5)]=0与T1[1]=5、S[(0,1)]=1，实际运行python -m pytest grading/test_t.py、test_s.py、test_connect.py、test_disconnect.py、test_integration.py全部通过（31项）；运行python -m src.run_experiment输出16 direction/frame checks passed，transfer_check.json中mismatches=0、latency_frames=1、conflict_rejected与release_ok、survivor_ok均为true；冲突前后snapshot相等、释放后两个端点回到IDLE且C2继续传送，均已在student_tests/test_my_case.py中用assert固定。
