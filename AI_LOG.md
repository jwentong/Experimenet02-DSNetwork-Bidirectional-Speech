# AI协作记录

## 需求
本次通过 GitHub Copilot 完成实验二的 T/S 交换、双向连接与释放函数，并添加了自拟回归测试。按要求不创建或填写实验报告模板；本文件仅记录 AI 协作过程。

## 建议与采纳
根据 README 和 `docs/model_contract.md`，实现遵循“输出指向输入”的映射约定：T 接线器重排同一链路内的时隙，S 接线器在同一时隙切换链路；TS0 和 TS16 保留透传，未连接业务输出填充 IDLE。建立连接时先验证端点与两方向的 T/S 资源冲突，只有检查全部通过才写入表；释放时只清除指定连接占用的资源。自拟测试覆盖释放后资源可复用，以及内部 T 资源冲突时拒绝新连接。

## 验证证据
C1 的手算映射为：A=(0,1)→B=(1,5) 对应 T0[5]=1、S[(1,5)]=0；反向对应 T1[1]=5、S[(0,1)]=1。可运行以下命令验证实现；此记录不宣称这些命令已经在本环境执行：

```bash
python -m pytest grading/test_t.py -q
python -m pytest grading/test_s.py -q
python -m pytest grading/test_connect.py -q
python -m pytest grading/test_disconnect.py -q
python -m pytest grading/test_integration.py -q
python -m pytest student_tests -q
python -m src.run_experiment
```
