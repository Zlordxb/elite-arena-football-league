"""
3. TEAM

A team owns a roster of HumanPlayer objects and can be
activated / deactivated (inactive teams cannot play matches).
"""

from .participant import Participant
from .player import HumanPlayer


class Team(Participant):
    def __init__(self, team_id, name):
        super().__init__(team_id, name)

        self.players = []
        self.is_active = True

    # ------------------------------------------------------------------ #
    # Roster management
    # ------------------------------------------------------------------ #
    def add_player(self, player):
        if not isinstance(player, HumanPlayer):
            raise TypeError("Only HumanPlayer objects can join a team.")

        if player.team is not None:
            raise ValueError(
                f"Player already belongs to team {player.team.name!r}."
            )

        if self.has_player(player.id):
            raise ValueError("Player ID already exists in this team.")

        self.players.append(player)
        player.team = self

    def remove_player(self, player_id):
        player = self.get_player(player_id)

        if player is None:
            raise ValueError("Player was not found in this team.")

        self.players.remove(player)
        player.team = None
        return player

    def get_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player

        return None

    def has_player(self, player_id):
        return self.get_player(player_id) is not None

    # ------------------------------------------------------------------ #
    # Status
    # ------------------------------------------------------------------ #
    def activate(self):
        if self.is_active:
            raise ValueError("Team is already active.")

        self.is_active = True

    def deactivate(self):
        if not self.is_active:
            raise ValueError("Team is already inactive.")

        self.is_active = False

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    @property
    def available_players(self):
        """Players who are allowed to take part in a match (not banned)."""
        return [p for p in self.players if p.is_available]

    @property
    def banned_players(self):
        return [p for p in self.players if p.is_banned]

    def get_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active,
            "players_count": len(self.players),
            "banned_count": len(self.banned_players),
        }
