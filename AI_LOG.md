# AI协作记录

## 需求

使用Claude Code（Opus 5）协助完成实验二。允许修改的文件限定为`src/t_switch.py`、`src/s_switch.py`、`src/connections.py`，以及自建的`student_tests/test_my_case.py`、`REPORT.md`、`AI_LOG.md`；不修改`src/models.py`、`src/engine.py`、`src/run_experiment.py`与`grading/`下任何教师测试，不改接口签名。要求AI先读`docs/model_contract.md`和函数docstring，说明控制表"输出→输入"、T→S固定路径、双向原子建立和一帧延迟这四个约定，再逐个函数补全。

## 建议与采纳

建议一：把时隙与链路合法性校验放在函数开头先整体执行，再生成输出数组，避免映射非法时留下半成品结果。采纳，因为教师测试`test_reserved_rejected`要求整条映射抛ValueError，先校验后构造更清晰。

建议二：`connect_pair`不要边检查边写表，先把两个方向的T输出`(src.link_id, dst.timeslot)`和S输出`(dst.link_id, dst.timeslot)`收集为计划，全部通过后一次性提交。采纳，`test_endpoint_conflict_atomic`等用例用`deepcopy`比对拒绝后tables是否完全不变。

建议三：端口占用按`(链路,时隙)`键判定，不要只按时隙号全局去重。采纳，`test_same_timeslot_other_links`允许(0,7)与(1,7)共存，按链路识别才正确。

建议四：AI曾建议在`connect_pair`里顺带校验控制表既有表项的完整性。修正为不采纳，教师框架保证表项由本函数写入，额外校验会改变既有行为并可能误报。

## 验证证据

先手算再核对：T单元`{1:3,3:1}`输入TS1=11、TS3=33，预期输出TS1=33、TS3=11；C1双向表为`T0[5]=1,S[(1,5)]=0;T1[1]=5,S[(0,1)]=1`；`sample_frame(0)`下A=3、B=116，预期输出帧1的B位置=3、A位置=116。

实际运行命令与结果：`.\.venv\Scripts\python.exe -m pytest grading/test_t.py -q` 6 passed；`test_s.py` 5 passed；`test_connect.py` 8 passed；`test_disconnect.py` 5 passed；`test_integration.py` 5 passed；`.\.venv\Scripts\python.exe -m src.run_experiment`输出"16 direction/frame checks passed; conflict rejected; release and surviving pair verified."；`.\.venv\Scripts\python.exe -m pytest student_tests -q` 4 passed；`.\.venv\Scripts\python.exe grading/run_grading.py --local`生成`.grade/grade_report.json`，实验70分项与报告30分项全部completed。

边界验证记录：映射保留时隙`{0:1}`、`{1:16}`、`{16:2}`与越界`{32:1}`、`{1:-1}`均抛ValueError且输入帧不变；S单元`{(2,1):0}`、`{(0,1):2}`、`{(0,16):1}`、`{(0,32):1}`抛ValueError；内部T输出争用返回False且`deepcopy`比对一致；重复释放返回False不影响其余连接；把数据字节改为0xD5后端点仍判定为占用。
