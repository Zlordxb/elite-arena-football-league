"""
5. FOOTBALL MATCH

Adds football-specific discipline rules on top of Match:
yellow cards, red cards, and automatic send-off after two yellows.
"""

from .constants import CardType, SendOffReason, YELLOW_CARDS_FOR_SEND_OFF
from .match import Match
from .player import HumanPlayer
from .validators import validate_choice


class FootballMatch(Match):
    def __init__(self, match_id, team1, team2):
        super().__init__(match_id, team1, team2)

        self.yellow_cards = []         # [HumanPlayer, ...] one entry per card
        self.red_cards = []            # [{"player": HumanPlayer, "reason": str}]
        self.yellow_count = {}         # {player_id: number of yellows}
        self.sent_off_players = set()  # {player_id, ...}

    # ------------------------------------------------------------------ #
    # Discipline
    # ------------------------------------------------------------------ #
    def add_card(self, player, card_type):
        # 1) Validate everything before touching any state.
        if not self.is_live:
            raise RuntimeError("Cards can only be given during live matches.")

        card_type = validate_choice(card_type, CardType.ALL, "Card type")

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
            self.yellow_cards.append(player)
            self.yellow_count[player.id] = self.yellow_count.get(player.id, 0) + 1

            # Two yellow cards result in a red card.
            if self.yellow_count[player.id] >= YELLOW_CARDS_FOR_SEND_OFF:
                self._send_off(player, SendOffReason.SECOND_YELLOW)

        else:  # CardType.RED
            self._send_off(player, SendOffReason.DIRECT_RED)

    def _send_off(self, player, reason):
        self.red_cards.append({"player": player, "reason": reason})
        self.sent_off_players.add(player.id)

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    def is_participating(self, player):
        return any(
            p is player for p in self.team1.players + self.team2.players
        )

    def is_sent_off(self, player):
        return player.id in self.sent_off_players

    def yellow_cards_for(self, player):
        return self.yellow_count.get(player.id, 0)

    def get_cards_report(self):
        """One row per card shown: yellows first, then reds."""
        report = [
            {
                "player": p.name,
                "team": p.team.name if p.team else "-",
                "card": CardType.YELLOW,
                "reason": "yellow",
            }
            for p in self.yellow_cards
        ]

        for entry in self.red_cards:
            player = entry["player"]
            report.append({
                "player": player.name,
                "team": player.team.name if player.team else "-",
                "card": CardType.RED,
                "reason": entry["reason"],
            })

        return report

    def get_match_details(self):
        return {
            "match_id": self.match_id,
            "team1": self.team1.name,
            "team2": self.team2.name,
            "score": self.score,
            "status": self.status,
            "yellow_cards": len(self.yellow_cards),
            "red_cards": len(self.red_cards),
            "sent_off_players": sorted(self.sent_off_players, key=str),
        }
