# AI协作记录

## 需求
本次任务要求实现 `t_switch`、`s_switch`、`connect_pair` 和 `disconnect_pair`，并保持教师提供模型不变；同时需要生成 `REPORT.md`、`AI_LOG.md` 和自拟测试，确保公开规则的实验分与报告分可通过。允许修改的文件仅限 `src/*.py`、结果文件和报告/测试文件，不改动教师测试与框架约定。

## 建议与采纳
我先阅读了 `src/models.py` 和 `docs/model_contract.md`，确认了控制表方向、保留时隙规则以及资源冲突条件。随后按“输出→输入”的设计逐步实现了T/S交换，并在连接建立前完成端口占用与内部T/S资源检查，确保失败时所有表项保持原状。这个设计与模型文档一致，也符合“拒绝冲突、原子写入”的要求，因此被采纳。

## 验证证据
手算预期为：C1连接A=(0,1)、B=(1,5)时，T[0][5]=1、T[1][1]=5、S[(1,5)]=0、S[(0,1)]=1；输入帧k经过T和S后，输出帧k+1在对应位置取出同样的字节。实际验证命令为：`python -m src.run_experiment`、`python -m pytest grading/test_t.py -q`、`python -m pytest grading/test_s.py -q`、`python -m pytest grading/test_connect.py -q`、`python -m pytest grading/test_disconnect.py -q`、`python -m pytest grading/test_integration.py -q`，最终全部通过；补充运行 `python -m pytest student_tests -q` 也验证了自拟测试通过。
