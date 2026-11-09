# AI协作记录
姓名：刘梓皓 学号：2024280422 GitHub：Kozeki0423 学生编号：34

工具与模型：Claude，用于辅助实现与检查。Deepseek v4.1 Flash。

## 需求

本次使用 Claude Code 作为 AI 协作工具，在教师提供的模板基础上补全 src/t_switch.py、src/s_switch.py、src/connections.py 中的四个函数，并完成自拟测试、结果文件和报告。允许修改的范围限定为这四个核心函数、student_tests、REPORT.md 与 AI_LOG.md；教师提供的 models.py、engine.py、run_experiment.py 与 grading 测试保持不变。

## 建议与采纳

AI 按“一次只完成一个函数”的顺序推进，先读 docstring 与模型约定再动手，这与 README 的要求一致，予以采纳。实现 connect_pair 时，AI 第一版把端点直接放进 set 判断端口占用，运行后 pytest 报 TypeError: unhashable type: 'Endpoint'，原因是 Endpoint 是未设置 frozen 的 dataclass，不可哈希。我判断这是 Python 层面的事实而非 AI 编造，于是改为先用 (link_id, timeslot) 元组构造占用集合再比较，修正后连接与释放测试全部通过。对于“先检查两个方向再一次性写表”的原子性要求，AI 建议把检查与写入分成两个循环，避免部分写入，这一点我阅读后认可并保留。

## 验证证据

手算预期：C1 的 A→B 需要 T0[5]=1、S[(1,5)]=0，B→A 需要 T1[1]=5、S[(0,1)]=1；输入帧 0 的 A 处字节为 3，应出现在输出帧 1 的链路 1 TS5。实际运行 .\.venv\Scripts\python.exe -m pytest grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py -q，结果 29 passed；运行 -m src.run_experiment 输出 16 direction/frame checks passed，transfer_check.json 中 checks=16、mismatches=0、conflict_rejected=true、release_ok=true、survivor_ok=true。自拟测试 python -m pytest student_tests -q 为 2 passed。首次实现正确后仍用内部阻塞与 IDLE 字节两个边界用例复核，未发现不一致。
