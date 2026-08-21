# PLAN.md
## 任务拆解
1. 实现Event数据模型 Event、Effect
2. 实现机器人迎宾主逻辑 RobotGreeterApplication
3. 编写单元测试用例，覆盖题目时序案例
4. 完成ARCHITECTURE.md架构文档
5. 完成REPORT.md问题排查文档
6. 完成AI_USAGE.md记录AI使用

## 时间规划
- 0‑15min：Fork仓库，创建分支，提交PLAN.md，创建Draft PR
- 15‑60min：编码实现业务逻辑
- 60‑95min：编写单元测试，调试修复bug
- 95‑110min：补齐三份md文档
- 110‑120min：检查全部文件，转为Ready for review

## 风险点
- 注意TICK事件无person_id；
- 并发多个人物状态隔离；
- 超时送客逻辑；
- Effect只返回本次触发的动作。
