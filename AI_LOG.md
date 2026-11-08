# AI协作记录

## 需求

2026-11-08，使用Codex协助完成实验二。本人已完成Fork与Clone，
要求AI阅读项目外提供的Word实验规范，在本地目录
E:\Prd\test2\Experimenet02-DSNetwork-Bidirectional-Speech
继续完成环境、四个核心函数、自拟测试、真实结果文件与报告，
完成后不push到GitHub，保留本地成果供本人检查。

实现范围为src/t_switch.py、src/s_switch.py、src/connections.py；
新增REPORT.md、AI_LOG.md、student_tests/test_my_case.py，
由原有src.run_experiment生成results中的两个JSON和PNG。
不修改教师提供的models、engine、run_experiment、grading测试及评分器。
未虚构姓名、学号或教师云端成绩。
报告首次生成时如实注明未获姓名和学号；收到本人明确回复后，
补齐REPORT.md署名并删除信息尚缺的过时说明。

## 建议与采纳

AI先读取Word原文、README、docs/model_contract.md及各函数docstring，
按规范先记录T/S和C1、C2的手算预期，再逐个函数实现和运行对应测试。
采纳输出→输入方向与固定T→S路径：T先把源字节放到目的时隙，
S再选择源链路的同一时隙，避免把S实现成时隙重排。

采纳先检查两个方向的端口、连接ID、内部T输出和S输出，
全部通过再写表的建议；不通过时返回False，不用回滚或部分提交。
资源占用查表而非比较PCM字节，因此合法的0xD5不能当作可抢占端口。
释放依据pairs中保存的端点，只删除该连接的两个方向，
未连接位置由T/S自然填入IDLE，不额外修改其他话路。

T/S增加精确帧形状、uint8类型和整数控制索引检查，返回独立的新数组；
TS0/16原位复制。没有改动教师缓存时序，输入帧k仍在输出帧k+1可用。
最终复核还对连接端口增加整数类型检查，拒绝浮点数、字符串和布尔值，
确保非法端口在连接时抛ValueError，而不是写表后在交换时失败。
四个函数首次对应公开测试均通过，未发生需要掩盖或编造的测试修复过程。
补充反向内部阻塞、S单独占用、相同映射也不共享、空闲值作为真实数据、
释放重用、非法索引和输入不变等反例，验证超出单纯成功连接的边界。

## 验证证据

建立.venv并按requirements.txt安装依赖，实际运行环境自检成功。
按顺序执行以下命令，所有python均使用.\.venv\Scripts\python.exe：

```text
python -m src.test_environment                        -> Environment OK
python -m pytest grading/test_environment.py -q       -> 2 passed
python -m pytest grading/test_t.py -q                 -> 6 passed
python -m pytest grading/test_s.py -q                 -> 5 passed
python -m pytest grading/test_connect.py -q           -> 8 passed
python -m pytest grading/test_disconnect.py -q        -> 5 passed
python -m pytest grading/test_integration.py -q       -> 5 passed
python -m src.run_experiment                          -> 16 checks passed
python -m pytest student_tests -q                     -> 49项通过（完整回归中）
python -m pytest grading student_tests -q             -> 90 passed
python grading/run_grading.py --local                 -> 100.0/100
```

手算输入帧0：A=3、B=116、C=6、D=119。读取实际transfer_check.json，
前四条输出为B=3、A=116、D=6、C=119；共16条记录，mismatches=0，
latency_frames=1，冲突拒绝、释放及存续连接标志均为true。
读取control_tables.json确认释放后仅留下C2的两组T/S映射。
自拟测试包含实际实验函数调用、明确断言和异常/输入不变检查，
最初43项通过，补充6项非法端口类型反例后共49项，完整回归90项全部通过。
实际本地评分为100.0/100，八个评分分组均全项通过；
结果可核对.grade/grade_report.json与.grade/grade_result.txt。
不把本地评分宣传为云端已评分或已提交。
