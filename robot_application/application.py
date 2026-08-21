from copy import deepcopy
from typing import List, Dict, Optional

from .models import Event, Effect


class RobotApplication:
    def __init__(self, absence_timeout_s: float = 10.0):
        self.absence_timeout_s = absence_timeout_s

        # 在场人员 {person_id: last_enter_ts}
        self.present_persons: Dict[str, float] = {}
        # 已离场待送客人员 {person_id: leave_timestamp}
        self.absent_pending_goodbye: Dict[str, float] = {}
        # 已经完成送客的人员，防止重复送客
        self.goodbye_done: set[str] = set()

        # 会话/会议标记，任意一个激活则屏蔽迎宾送客
        self.in_conversation: bool = False
        self.in_meeting: bool = False

        # 已经完成迎宾的人（本次在场周期内）
        self.greeted_set: set[str] = set()

    def snapshot(self):
        """返回深拷贝，外部修改不会影响内部状态"""
        return deepcopy({
            "present_persons": self.present_persons,
            "absent_pending_goodbye": self.absent_pending_goodbye,
            "goodbye_done": self.goodbye_done,
            "in_conversation": self.in_conversation,
            "in_meeting": self.in_meeting,
            "greeted_set": self.greeted_set
        })

    def handle_event(self, event: Event) -> List[Effect]:
        output: List[Effect] = []
        et = event.event_type
        pid = event.person_id
        ts = event.timestamp

        # ========== 会话、会议状态更新 ==========
        if et == "CONVERSATION_STARTED":
            self.in_conversation = True
        elif et == "CONVERSATION_ENDED":
            self.in_conversation = False
        elif et == "MEETING_STARTED":
            self.in_meeting = True
        elif et == "MEETING_ENDED":
            self.in_meeting = False

        # 是否处于抑制模式：会话or会议中，禁止迎宾送客
        suppress_action = self.in_conversation or self.in_meeting

        # ========== PERSON_ENTERED 人员进入 ==========
        if et == "PERSON_ENTERED" and pid is not None:
            # 如果此人在待送客列表：离开不足10秒就返回，清除待送客，不迎宾
            if pid in self.absent_pending_goodbye:
                del self.absent_pending_goodbye[pid]
            else:
                # 全新进入，不在场
                if pid not in self.present_persons:
                    self.present_persons[pid] = ts
                    # 不在会话会议，且本轮没迎宾过，执行迎宾
                    if not suppress_action and pid not in self.greeted_set:
                        output.append(Effect(
                            effect_type="wave_hand",
                            value="欢迎光临",
                            reason="空闲时人员首次进入"
                        ))
                        self.greeted_set.add(pid)

        # ========== PERSON_LEFT 人员离开 ==========
        elif et == "PERSON_LEFT" and pid is not None:
            if pid in self.present_persons:
                del self.present_persons[pid]
                self.absent_pending_goodbye[pid] = ts

        # ========== TICK 时间推进，处理送客逻辑 ==========
        elif et == "TICK":
            to_remove = []
            for abs_pid, leave_ts in self.absent_pending_goodbye.items():
                delta = ts - leave_ts
                # 离开满超时时间，且没有送过，且不在会话会议
                if delta >= self.absence_timeout_s and abs_pid not in self.goodbye_done:
                    if not suppress_action:
                        output.append(Effect(
                            effect_type="wave_hand",
                            value="送客一次",
                            reason="人员离开满10秒，TICK触发送客"
                        ))
                    self.goodbye_done.add(abs_pid)
                # 已经完成送客，清理待送客列表
                if abs_pid in self.goodbye_done:
                    to_remove.append(abs_pid)
            for p in to_remove:
                if p in self.absent_pending_goodbye:
                    del self.absent_pending_goodbye[p]

            # 清理已经送客完毕的集合，允许下次重新入场重新迎宾
            for finished_pid in list(self.goodbye_done):
                if finished_pid not in self.absent_pending_goodbye:
                    self.greeted_set.discard(finished_pid)

        return output
