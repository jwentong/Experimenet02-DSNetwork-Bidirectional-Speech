# AI协作记录

## 需求

本次要求补全四个函数：src/t_switch.py 的 t_switch（按输出→输入重排时隙）、src/s_switch.py 的 s_switch（同一时隙选择输入链路）、src/connections.py 的 connect_pair 与 disconnect_pair（双向建立与释放），并保持教师接口不变。允许修改的只有这三个任务文件，教师提供的 models.py、engine.py、run_experiment.py 与 grading 测试不得改动，也不得修改评分脚本。

## 建议与采纳

先阅读 docs/model_contract.md 与各函数 docstring，明确控制表统一「输出→输入」、资源占用看控制表而非字节值、固定先 T 后 S 且一帧缓存。采纳「一次只补全一个函数」的建议：先实现 t_switch 与 s_switch 并跑对应测试，再实现 connect_pair 时先做全部检查（重复 ID、端点占用、T 输出与 S 输出冲突）后原子写入，最后实现 disconnect_pair 按 pairs 定位并删除两个方向。内部阻塞反例（C1 存在时请求 (0,2)、(0,5)）提醒我在 connect_pair 里单独检查 T 输出冲突，不能只判断端点是否被占。

## 验证证据

手算 C1 与 C2 的控制表与帧 0 字节（A=3、B=116、C=6、D=119），与 results/transfer_check.json 的 16 条记录一致。运行 `pytest grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py grading/test_environment.py -q` 得到 31 passed；`python -m src.run_experiment` 输出 16 direction/frame checks passed；`pytest student_tests -q` 通过自拟内部阻塞与释放重用两个用例。
