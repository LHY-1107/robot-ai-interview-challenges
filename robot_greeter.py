from dataclasses import dataclass
from enum import Enum
import time


class EventType(Enum):
    PERSON_ENTER = "PERSON_ENTER"
    PERSON_LEAVE = "PERSON_LEAVE"
    TICK = "TICK"


@dataclass
class Event:
    event_type: EventType
    person_id: str = None
    timestamp: float = None


class RobotGreeterApplication:
    def __init__(self, greet_delay: float = 2.0):
        self.greet_delay = greet_delay
        self.person_enter_time = dict()
        self.greeted_person = set()

    def handle_event(self, event: Event) -> list[str]:
        outputs = []
        if event.event_type == EventType.PERSON_ENTER:
            self.person_enter_time[event.person_id] = event.timestamp
        elif event.event_type == EventType.PERSON_LEAVE:
            if event.person_id in self.person_enter_time:
                del self.person_enter_time[event.person_id]
            if event.person_id in self.greeted_person:
                self.greeted_person.remove(event.person_id)
        elif event.event_type == EventType.TICK:
            now = event.timestamp
            for pid in list(self.person_enter_time.keys()):
                enter_ts = self.person_enter_time[pid]
                if pid not in self.greeted_person and (now - enter_ts) >= self.greet_delay:
                    outputs.append(f"Hello {pid}!")
                    self.greeted_person.add(pid)
        return outputs
