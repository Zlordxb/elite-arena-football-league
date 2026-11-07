"""
Event log: the "history" of a tournament or a match.

Every meaningful action (a team joins, a match kicks off, a card is shown,
a player is banned, ...) is recorded as an Event so the UI can show a
timeline and exports can replay what happened.
"""

import itertools
from dataclasses import dataclass, field
from datetime import datetime


class EventType:
    TEAM_REGISTERED = "team_registered"
    TEAM_REMOVED = "team_removed"
    TEAM_ACTIVATED = "team_activated"
    TEAM_DEACTIVATED = "team_deactivated"
    PLAYER_ADDED = "player_added"
    PLAYER_REMOVED = "player_removed"
    PLAYER_BANNED = "player_banned"
    PLAYER_UNBANNED = "player_unbanned"
    SCHEDULE_GENERATED = "schedule_generated"
    MATCH_STARTED = "match_started"
    CARD = "card"
    SEND_OFF = "send_off"
    MATCH_FINISHED = "match_finished"

    LABELS = {
        TEAM_REGISTERED: "Team registered",
        TEAM_REMOVED: "Team removed",
        TEAM_ACTIVATED: "Team activated",
        TEAM_DEACTIVATED: "Team deactivated",
        PLAYER_ADDED: "Player added",
        PLAYER_REMOVED: "Player removed",
        PLAYER_BANNED: "Player banned",
        PLAYER_UNBANNED: "Player unbanned",
        SCHEDULE_GENERATED: "Schedule generated",
        MATCH_STARTED: "Kick-off",
        CARD: "Card",
        SEND_OFF: "Sent off",
        MATCH_FINISHED: "Full time",
    }

    ALL = tuple(LABELS)

    # Groups used by timeline filters.
    MATCH_EVENTS = (MATCH_STARTED, CARD, SEND_OFF, MATCH_FINISHED)
    TEAM_EVENTS = (TEAM_REGISTERED, TEAM_REMOVED, TEAM_ACTIVATED, TEAM_DEACTIVATED)
    PLAYER_EVENTS = (PLAYER_ADDED, PLAYER_REMOVED, PLAYER_BANNED, PLAYER_UNBANNED)


# Events created in the same instant still get a stable order.
_sequence = itertools.count(1)


@dataclass
class Event:
    type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: dict = field(default_factory=dict)
    sequence: int = field(default_factory=lambda: next(_sequence))

    @property
    def label(self):
        return EventType.LABELS.get(self.type, self.type)

    @property
    def sort_key(self):
        return (self.timestamp, self.sequence)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
            "type": self.type,
            "label": self.label,
            "message": self.message,
            **self.data,
        }


class EventLog:
    def __init__(self):
        self._events = []

    def record(self, event_type, message, **data):
        if event_type not in EventType.ALL:
            raise ValueError(f"Unknown event type: {event_type!r}.")

        if not isinstance(message, str) or not message.strip():
            raise ValueError("Event message cannot be empty.")

        event = Event(event_type, message.strip(), data=data)
        self._events.append(event)
        return event

    @property
    def events(self):
        return list(self._events)

    def latest(self, limit=10):
        """Most recent events first."""
        return list(reversed(self._events))[:limit]

    def of_type(self, *event_types):
        return [e for e in self._events if e.type in event_types]

    def __len__(self):
        return len(self._events)

    def __iter__(self):
        return iter(self._events)
