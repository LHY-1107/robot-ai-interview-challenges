# Architecture Design

## Overview
RobotGreeterApplication 是一个事件驱动的迎宾机器人业务模块，接收三类事件：人员进入、人员离开、时间节拍TICK，在人员停留达到设定延时后输出问候语，同一人在场期间只问候一次。

## Core Components
1. **EventType**：事件枚举，定义三种事件类型
    - PERSON_ENTER：人员进入场景
    - PERSON_LEAVE：人员离开场景
    - TICK：时间节拍，驱动业务逻辑判断
2. **Event**：数据实体，封装事件类型、人员ID、时间戳
3. **RobotGreeterApplication**：核心业务类
    - `greet_delay`：配置问候等待延时
    - `person_enter_time`：字典，记录每个人进入的时间戳
    - `greeted_person`：集合，记录已经完成问候的人员，避免重复问候
    - `handle_event(event)`：入口方法，接收事件，返回输出字符串列表

## Workflow
1. 收到 `PERSON_ENTER`：记录该人员进入时间
2. 收到 `PERSON_LEAVE`：清除该人员全部状态，离开后再次进入可以重新触发问候
3. 收到 `TICK`：遍历在场人员，对比当前时间与进入时间；满足延时且未问候过，则生成问候输出，标记已问候
4. 一次TICK可同时对多个人输出问候

## Data Flow
`外部事件源 → Event对象 → RobotGreeterApplication.handle_event() → 输出问候字符串列表`

## State Management
- 内存维护两份状态：进入时间字典、已问候人员集合
- 人员离开时清理对应状态，保证重复进出逻辑正确
- 无持久化，进程重启状态全部丢失

## Test Strategy
使用unittest单元测试覆盖核心场景：
1. 停留达到延时正常输出问候
2. 同一人在场不会重复问候
3. 人员离开后再次进入，可再次问候
4. 未到延时就离开，不会产生问候
