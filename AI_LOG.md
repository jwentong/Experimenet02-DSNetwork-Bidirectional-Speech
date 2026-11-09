## 需求
补全 T/S 交换、双向连接建立与释放函数。

## 建议与采纳
AI 建议使用 numpy 数组保证 dtype 为 uint8，连接建立采用“先全量检查，后统一写入”保证原子性。采纳了双向映射的遍历逻辑。修正了初始版本中返回普通 list 导致的测试失败问题，改为了 numpy.full 分配。

## 验证证据
运行了 pytest grading/test_t.py 等共 31 项公开测试全部通过；运行了 run_experiment 成功生成 3 个 results 产物，16 次核对无错。