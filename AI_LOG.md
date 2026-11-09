# AI协作记录

## 需求
本次实验使用了AI助手进行辅助开发。实验要求在不修改教师提供的 grading/ 测试代码和接口的前提下，补全 src/t_switch.py、src/s_switch.py 以及 src/connections.py 中的四个核心函数。允许修改和提交的文件包括上述三个源文件、REPORT.md、AI_LOG.md、自拟测试文件以及 results/ 下生成的产物。

## 建议与采纳
数组初始化建议：在编写 T 交换时，AI建议使用 numpy.full 来创建默认值为 IDLE 的 uint8 数组，并提醒必须严格校验控制表是否越界或包含了保留时隙。我采纳了该建议，因为它能确保数据类型匹配且提升了程序的健壮性。

双向连接原子性建议：在编写 connect_pair 时，AI特别强调了“双向原子建立”原则，建议先用 for 循环检查两端端口占用、内部 T 表和 S 表资源冲突，确认全部通过后，再一次性将四条映射写入控制表，失败时必须保持表原样。我采纳了此建议，有效避免了产生“半连接”的脏数据。

缩进错误修正：在首次编写代码时，由于复制粘贴导致函数体没有正确缩进，终端报了 IndentationError。AI分析日志后指出了缩进问题，我修正后测试顺利通过。

## 验证证据
手算预期：双向连接 A=(0,1) 到 B=(1,5) 时，正向映射应为 T0[5]=1 和 S[(1,5)]=0。输入帧k的数据应在输出帧k+1中出现。
实际运行命令及结果：

运行 .\.venv\Scripts\python.exe -m pytest grading/test_t.py -q，结果 6 passed。

运行 .\.venv\Scripts\python.exe -m pytest grading/test_s.py -q，结果 5 passed。

运行 .\.venv\Scripts\python.exe -m pytest grading/test_connect.py -q 和 test_disconnect.py -q，结果均全绿通过。

最后运行集成测试及仿真入口，生成的 transfer_check.json 成功通过 16 次数据校验，证明一帧延迟与控制表读写逻辑完全正确。
