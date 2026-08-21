import unittest
from robot_greeter import RobotGreeterApplication, Event, EventType


class TestRobotGreeter(unittest.TestCase):
    def setUp(self):
        self.app = RobotGreeterApplication(greet_delay=2.0)

    def test_greet_after_delay(self):
        # 人进入
        e1 = Event(event_type=EventType.PERSON_ENTER, person_id="alice", timestamp=0.0)
        res1 = self.app.handle_event(e1)
        self.assertEqual(res1, [])

        # TICK时间不足，不打招呼
        e2 = Event(event_type=EventType.TICK, timestamp=1.0)
        res2 = self.app.handle_event(e2)
        self.assertEqual(res2, [])

        # TICK时间超过延时，输出问候
        e3 = Event(event_type=EventType.TICK, timestamp=2.5)
        res3 = self.app.handle_event(e3)
        self.assertEqual(res3, ["Hello alice!"])

        # 再次TICK，不能重复问候
        e4 = Event(event_type=EventType.TICK, timestamp=3.0)
        res4 = self.app.handle_event(e4)
        self.assertEqual(res4, [])

    def test_person_leave_clear_state(self):
        e1 = Event(event_type=EventType.PERSON_ENTER, person_id="bob", timestamp=0.0)
        self.app.handle_event(e1)

        e_tick = Event(event_type=EventType.TICK, timestamp=3.0)
        self.app.handle_event(e_tick)

        # 离开
        e_leave = Event(event_type=EventType.PERSON_LEAVE, person_id="bob", timestamp=4.0)
        self.app.handle_event(e_leave)

        # 再次进入，允许重新问候
        e_reenter = Event(event_type=EventType.PERSON_ENTER, person_id="bob", timestamp=5.0)
        self.app.handle_event(e_reenter)
        e_tick2 = Event(event_type=EventType.TICK, timestamp=7.5)
        res = self.app.handle_event(e_tick2)
        self.assertEqual(res, ["Hello bob!"])

    def test_leave_before_greet(self):
        e1 = Event(event_type=EventType.PERSON_ENTER, person_id="charlie", timestamp=0.0)
        self.app.handle_event(e1)
        e_leave = Event(event_type=EventType.PERSON_LEAVE, person_id="charlie", timestamp=1.0)
        self.app.handle_event(e_leave)
        e_tick = Event(event_type=EventType.TICK, timestamp=3.0)
        res = self.app.handle_event(e_tick)
        self.assertEqual(res, [])


if __name__ == '__main__':
    unittest.main()
