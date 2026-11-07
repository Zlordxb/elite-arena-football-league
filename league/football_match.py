"""
5. FOOTBALL MATCH

Adds football-specific discipline rules on top of Match:
yellow cards, red cards (with the minute they were shown),
and automatic send-off after two yellows.
"""

from datetime import datetime

from .constants import (
    MAX_MATCH_MINUTE,
    YELLOW_CARDS_FOR_SEND_OFF,
    CardType,
    SendOffReason,
)
from .events import EventType
from .match import Match
from .player import HumanPlayer
from .validators import validate_choice, validate_minute


class FootballMatch(Match):
    def __init__(self, match_id, team1, team2):
        super().__init__(match_id, team1, team2)

        # Every card shown, in order. Each record:
        # {"player", "team", "card", "reason", "minute", "timestamp"}
        self.cards = []
        self.yellow_count = {}          # {player_id: number of yellows}
        self.sent_off_players = set()   # {player_id, ...}

    # ------------------------------------------------------------------ #
    # Discipline
    # ------------------------------------------------------------------ #
    def add_card(self, player, card_type, minute=None):
        """
        Show a card to `player`. Returns the card record that was created.
        Two yellow cards automatically produce a red card (send-off).
        """
        # 1) Validate everything before touching any state.
        if not self.is_live:
            raise RuntimeError("Cards can only be given during live matches.")

        card_type = validate_choice(card_type, CardType.ALL, "Card type")
        minute = validate_minute(minute, MAX_MATCH_MINUTE)

        if not isinstance(player, HumanPlayer):
            raise TypeError("A valid HumanPlayer object is required.")

        if not self.is_participating(player):
            raise ValueError(
                "Player does not belong to either team in this match."
            )

        if player.is_banned:
            raise ValueError("A banned player cannot participate.")

        if self.is_sent_off(player):
            raise ValueError("This player has already been sent off.")

        # 2) Apply the card.
        if card_type == CardType.YELLOW:
            record = self._record_card(player, CardType.YELLOW, "yellow", minute)
            self.yellow_count[player.id] = self.yellow_count.get(player.id, 0) + 1

            # Two yellow cards result in a red card.
            if self.yellow_count[player.id] >= YELLOW_CARDS_FOR_SEND_OFF:
                self._send_off(player, SendOffReason.SECOND_YELLOW, minute)

            return record

        return self._send_off(player, SendOffReason.DIRECT_RED, minute)

    def _record_card(self, player, card_type, reason, minute):
        record = {
            "player": player,
            "team": player.team,
            "card": card_type,
            "reason": reason,
            "minute": minute,
            "timestamp": datetime.now(),
        }
        self.cards.append(record)

        self.events.record(
            EventType.CARD,
            f"{card_type.title()} card: {player.name} ({self._team_name(player)})"
            f"{self._minute_text(minute)}.",
            match_id=self.match_id,
            matchday=self.matchday,
            player_id=player.id,
            player=player.name,
            team=self._team_name(player),
            card=card_type,
            minute=minute,
        )
        return record

    def _send_off(self, player, reason, minute):
        record = self._record_card(player, CardType.RED, reason, minute)
        self.sent_off_players.add(player.id)

        why = "second yellow" if reason == SendOffReason.SECOND_YELLOW else "direct red"
        self.events.record(
            EventType.SEND_OFF,
            f"{player.name} ({self._team_name(player)}) sent off ({why})"
            f"{self._minute_text(minute)}.",
            match_id=self.match_id,
            matchday=self.matchday,
            player_id=player.id,
            player=player.name,
            team=self._team_name(player),
            reason=reason,
            minute=minute,
        )
        return record

    @staticmethod
    def _team_name(player):
        return player.team.name if player.team else "-"

    @staticmethod
    def _minute_text(minute):
        return f" {minute}'" if minute is not None else ""

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    @property
    def yellow_cards(self):
        """Players who received a yellow card (one entry per card)."""
        return [c["player"] for c in self.cards if c["card"] == CardType.YELLOW]

    @property
    def red_cards(self):
        """One {"player", "reason"} entry per red card."""
        return [
            {"player": c["player"], "reason": c["reason"]}
            for c in self.cards
            if c["card"] == CardType.RED
        ]

    def is_participating(self, player):
        return any(
            p is player for p in self.team1.players + self.team2.players
        )

    def is_sent_off(self, player):
        return player.id in self.sent_off_players

    def yellow_cards_for(self, player):
        return self.yellow_count.get(player.id, 0)

    def cards_for_team(self, team, card_type=None):
        return [
            c for c in self.cards
            if c["team"] is team and (card_type is None or c["card"] == card_type)
        ]

    def get_cards_report(self):
        """One row per card shown, in the order they were given."""
        return [
            {
                "minute": c["minute"],
                "player": c["player"].name,
                "team": c["team"].name if c["team"] else "-",
                "card": c["card"],
                "reason": c["reason"],
            }
            for c in self.cards
        ]

    def get_match_details(self):
        return {
            "match_id": self.match_id,
            "matchday": self.matchday,
            "team1": self.team1.name,
            "team2": self.team2.name,
            "score": self.score,
            "status": self.status,
            "yellow_cards": len(self.yellow_cards),
            "red_cards": len(self.red_cards),
            "sent_off_players": sorted(self.sent_off_players, key=str),
        }
