from robot_application.models import Event
from robot_application.application import RobotApplication


def test_sample_case():
    """原题给的样例时序测试"""
    app = RobotApplication(absence_timeout_s=10.0)
    effects = []
    # 0 PERSON_ENTERED
    effects.extend(app.handle_event(Event("PERSON_ENTERED", timestamp=0, person_id="u1")))
    assert len(effects) == 1
    assert effects[0].value == "欢迎光临"

    # 1 PERSON_ENTERED
    effects.clear()
    effects.extend(app.handle_event(Event("PERSON_ENTERED", timestamp=1, person_id="u1")))
    assert len(effects) == 0

    #2 CONVERSATION_STARTED
    effects.clear()
    effects.extend(app.handle_event(Event("CONVERSATION_STARTED", timestamp=2)))
    assert len(effects) == 0

    #3 PERSON_ENTERED
    effects.clear()
    effects.extend(app.handle_event(Event("PERSON_ENTERED", timestamp=3, person_id="u2")))
    assert len(effects) == 0

    #4 CONVERSATION_ENDED
    effects.clear()
    effects.extend(app.handle_event(Event("CONVERSATION_ENDED", timestamp=4)))
    assert len(effects) == 0

    #5 PERSON_LEFT
    effects.clear()
    effects.extend(app.handle_event(Event("PERSON_LEFT", timestamp=5, person_id="u1")))
    assert len(effects) == 0

    #14 TICK
    effects.clear()
    effects.extend(app.handle_event(Event("TICK", timestamp=14)))
    assert len(effects) == 0

    #15 TICK 触发送客
    effects.clear()
    effects.extend(app.handle_event(Event("TICK", timestamp=15)))
    assert len(effects) == 1
    assert effects[0].value == "送客一次"

    #16 TICK，不再重复送客
    effects.clear()
    effects.extend(app.handle_event(Event("TICK", timestamp=16)))
    assert len(effects) == 0

    #20 PERSON_ENTERED，再次入场重新迎宾
    effects.clear()
    effects.extend(app.handle_event(Event("PERSON_ENTERED", timestamp=20, person_id="u1")))
    assert len(effects) == 1
    assert effects[0].value == "欢迎光临"


def test_leave_less_10s_return():
    """离开不足10秒返回，不送客，不重复迎宾"""
    app = RobotApplication(10.0)
    app.handle_event(Event("PERSON_ENTERED", 0, "u1"))
    app.handle_event(Event("PERSON_LEFT", 2, "u1"))
    # 7秒就回来，不足10s
    eff = app.handle_event(Event("PERSON_ENTERED", 7, "u1"))
    assert len(eff) == 0


def test_conversation_suppress():
    """会话期间屏蔽迎宾送客"""
    app = RobotApplication(10.0)
    app.handle_event(Event("CONVERSATION_STARTED", 1))
    eff = app.handle_event(Event("PERSON_ENTERED", 2, "u1"))
    assert len(eff) == 0


def test_snapshot_isolation():
    """snapshot返回拷贝，外部修改不影响内部状态"""
    app = RobotApplication()
    app.handle_event(Event("PERSON_ENTERED", 0, "u1"))
    snap = app.snapshot()
    snap["present_persons"].clear()
    assert len(app.present_persons) == 1
