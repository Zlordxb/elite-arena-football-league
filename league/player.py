"""
2. HUMAN PLAYER

A player has a role (position), can be banned / unbanned,
and belongs to at most one team at a time.
"""

from .constants import PLAYER_ROLES
from .participant import Participant
from .validators import validate_choice


class HumanPlayer(Participant):
    def __init__(self, player_id, name, role):
        super().__init__(player_id, name)

        self.role = validate_choice(role, PLAYER_ROLES, "Player role")
        self.is_banned = False

        # Set by Team.add_player / cleared by Team.remove_player.
        self.team = None

    # ------------------------------------------------------------------ #
    # Discipline
    # ------------------------------------------------------------------ #
    def ban(self):
        if self.is_banned:
            raise ValueError("Player is already banned.")

        self.is_banned = True

    def unban(self):
        if not self.is_banned:
            raise ValueError("Player is not banned.")

        self.is_banned = False

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    @property
    def is_available(self):
        """A player can take part in a match only when not banned."""
        return not self.is_banned

    def get_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "is_banned": self.is_banned,
            "team": self.team.name if self.team else None,
        }
