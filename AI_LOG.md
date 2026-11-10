# AI协作记录
## 需求
使用AI辅助本次T‑S数字交换网络实验，允许修改文件：`src/t_switch.py`、`src/s_switch.py`、`src/connections.py`、`student_tests/test_my_case.py`、`REPORT.md`。本人完成核心业务逻辑，AI用于排错调试、分析报错、辅助撰写测试用例与实验文档。

## 建议与采纳
1. 建议：区分`t_maps`为字典类型，修改资源冲突判断逻辑，释放时使用pop删除表项。
判断：采纳
理由：前期误把t_maps当作列表，运行出现KeyError，调整为字典对应的判断与删除方式后，单元测试报错消除，符合框架数据结构。

2. 建议：自拟测试不手动构造Tables对象，只针对T、S接线器编写测试用例。
判断：采纳
理由：框架未开放Tables构造接口，手动构造字典会产生属性访问异常，只测试T/S模块即可满足自拟测试评分要求。

3. 建议：双向连接建立遵循原子性原则，全部资源校验通过之后再写入T、S控制表。
判断：采纳
理由：防止出现单向半连接，冲突时保证tables完全不发生改动，符合实验文档规定。

## 验证证据
手算双向连接A(0,3)↔B(1,5)：
预期：`t_maps[0][5]=3`，`t_maps[1][3]=5`，`s_map[(1,5)]=0`，`s_map[(0,3)]=1`。

运行命令：
python -m pytest grading/test_connect.py -q
python -m pytest grading/test_disconnect.py -q
python -m pytest student_tests -q
python -m src.run_experiment

实际结果：连接、释放全套官方测试全部通过；自拟5个测试用例全部PASS；完整仿真16次数据校验成功，生成`control_tables.json`、`transfer_check.json`与`switch_mapping.png`，运行结果和手算预期一致。
