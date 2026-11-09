# AI协作记录

## 需求
使用 DeepSeek 编程助手辅助实现 `src/t_switch.py`、`src/s_switch.py`、`src/connections.py` 中的四个待实现函数；只修改这些任务文件，不改教师测试与评分脚本。

## 建议与采纳
AI 建议 T 交换“以 IDLE 填充新帧、TS0/16 原位透传、再按控制表覆盖”，S 交换“只改链路不改时隙、各链路 TS0/16 透传”，连接建立采用“先检查两个方向、全部通过后一次性写入”的原子处理。本人核对 `docs/model_contract.md` 与测试后采纳，并补充了“端点占用按 (链路,时隙) 判断、重复 ID/内部 T/S 冲突返回 False”的边界。

## 验证证据
手算 C1 的双向控制表（T0[5]=1、S[(1,5)]=0；T1[1]=5、S[(0,1)]=1），并用 sample_frame(0) 核对 A=3、B=116 的去向。实际运行 `python -m pytest grading/test_t.py grading/test_s.py grading/test_connect.py grading/test_disconnect.py grading/test_integration.py -q` 全部通过；运行 `python -m src.run_experiment` 生成两个 JSON 与一张 PNG，16 次校验零错配、冲突被拒绝、释放与保留连接均正确。
