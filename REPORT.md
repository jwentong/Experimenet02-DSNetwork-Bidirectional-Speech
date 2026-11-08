# 实验二报告

姓名：巴达伟·安努尔
学号：2022280592

## 原理与手算

本实验的每条链路由每帧32个8 bit PCM样本组成，帧率为8000帧/s，
所以每帧125 μs，每链路总码率为32×8×8000=2.048 Mbit/s，
一个时隙通道为64 kbit/s。TS0与TS16在本模型中保留并原位透传，
其余30个位置为业务时隙。未连接业务输出填0xD5，资源占用必须查控制表。

T接线器改变同一链路内的时隙，控制表按“输出→输入”解释。
手算：输入TS1=11、TS3=33，映射{1:3, 3:1}，应输出TS1=33、TS3=11。
S接线器在同一时隙选择输入链路，不改变时隙号。
手算：输入帧0的链路0 TS3=9、链路1 TS3=110，
映射{(0,3):1, (1,3):0}，应输出链路0 TS3=110、链路1 TS3=9。

C1连接A=(0,1)、B=(1,5)：A→B需要T0[5]=1、S[(1,5)]=0；
B→A需要T1[1]=5、S[(0,1)]=1。
C2连接C=(0,2)、D=(1,6)：C→D需要T0[6]=2、S[(1,6)]=0；
D→C需要T1[2]=6、S[(0,2)]=1。
按sample_frame(k)=(link×101+slot×3+k×17) mod 256，
输入帧0中A=3、B=116、C=6、D=119，应在输出帧1对应得到
B=3、A=116、D=6、C=119。T→S组合总延迟为一帧，S不额外增加一帧。

## 结果分析

实际运行src.run_experiment，生成以下三个产物，未复制教师参考结果：

- results/transfer_check.json：四帧×两对连接×两个方向，共16条实际传送记录，
  mismatches=0、latency_frames=1；各记录available_frame_id均为input_frame_id+1。
  conflict_rejected、release_ok、survivor_ok均为true。
- results/control_tables.json：释放前T0={5:1,6:2}、T1={1:5,2:6}，
  S={(1,5):0,(0,1):1,(1,6):0,(0,2):1}，pairs包含C1与C2。
  释放C1后T0={6:2}、T1={2:6}、S={(1,6):0,(0,2):1}，仅保留C2。
- results/switch_mapping.png：输入帧0的两条链路与四个已连接业务输出可视化。
  图中输出对应输入帧0在输出帧1可用的结果，印证A/B与C/D交换字节。

输入帧0的四个实际输出为B=3、A=116、D=6、C=119，与手算一致。
资源冲突拒绝后原连接仍传送；释放C1后其两端回到IDLE，C2仍保持双向传送。
这些结论由逐字节比较及释放后再次交换得到，不能仅由控制表存在推断。

## 反例与验证

自拟测试先确定以下输入和预期，再编写实际调用实验函数的断言：

- 反向内部阻塞：C1已存在，再请求(0,5)与(0,2)。前向资源可用，
  反向仍需已占用的T0输出TS5，应返回False，三张表及原话路完全不变。
- 仅S输出冲突：预占s_map[(0,2)]，请求(0,2)与(1,6)，
  两个T输出虽为空也必须整体拒绝；不能先写入前向表项。
- 合法样本等于0xD5：令A输入字节等于IDLE，仍正常传送且端口继续占用。
- 释放与重用：C1、C2共存时释放C1，两端输出应空闲，C2仍双向传送；
  重复释放应返回False，原端点和内部资源应可重新建立连接。
- 无效控制表、保留时隙、错误帧形状或数据类型应明确报错且不修改输入。
- 同一时隙跨链路连接与同链路双向连接应分别按链路及完整端口识别。

自拟用例位于student_tests/test_my_case.py，包括16个test_函数，
参数化展开后的用例覆盖反向T冲突，特意把可用方向
放在前面，确保不能在发现第二方向被占用之前写入第一方向；
S冲突也分别覆盖两个方向。深拷贝整个Tables比较，验证拒绝时三张表均不变。
此外通过输入副本和shares_memory检查验证T/S返回新数组并保留原输入，
覆盖字节0、0xD5、255，以及业务边界TS31。
端口反例也覆盖浮点数、字符串与布尔值；非法端口标识应在连接阶段
抛ValueError，不能建立无效表项后等到数据交换才报错。
最终16个自拟测试函数经参数化展开为49项，全部通过。

全部命令在项目根目录，以本项目.venv解释器运行：

```powershell
.\.venv\Scripts\python.exe -m src.test_environment
.\.venv\Scripts\python.exe -m pytest grading/test_environment.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_t.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_s.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_connect.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_disconnect.py -q
.\.venv\Scripts\python.exe -m pytest grading/test_integration.py -q
.\.venv\Scripts\python.exe -m src.run_experiment
.\.venv\Scripts\python.exe -m pytest student_tests -q
.\.venv\Scripts\python.exe -m pytest grading student_tests -q
.\.venv\Scripts\python.exe grading/run_grading.py --local
```

环境自检显示Environment OK；各公开分项依次通过2、6、5、8、5、5项，
合计31项。仿真输出“16 direction/frame checks passed”，
并明确验证冲突拒绝、释放及存续连接。
完整回归命令得到90 passed，包括31项环境/核心/集成测试、
49项自拟测试、6项学生交付检查和4项教师自动化开发测试。
本地公开规则预评分为100.0/100，八个评分分组均完成且全项通过，
结果记录在.grade/grade_report.json与.grade/grade_result.txt。
这些结果仅表示本机公开规则的预览，不能代替教师云端重新评分。
教师模型、帧推进、仿真入口、测试和评分器均保持原样。

本次按要求保留本地成果，不执行GitHub推送、创建教师PR或线上评分。
报告署名采用本人明确提供的真实姓名与完整学号，
未把Git昵称或工具账户名称当作课程身份。

## 局限

本模型固定先T后S，端口均空闲仍可能因内部T输出被占用而发生阻塞；
不实现多级网络、备用路径搜索或重排已有连接。整帧缓存的一帧延迟
是离线仿真的时序约定，available_frame_id标注结果可用帧，
不是要求Python每125 μs实时唤醒，也不代表所有真实T接线器的物理延迟。
TS0/TS16原位透传是课程配置，不实现真实E1帧同步或信令编码。
尚未实现呼叫状态机、SIP、实际电话或麦克风、PCM编解码及并发改表；
连接表变更仅发生在两次exchange_frame调用之间。
实验一128 bit/tick资源服务模型不能替代本实验的物理链路速率。
