"""
Sample data used by the console demo (main.py) and the
"Load sample league" button in the Streamlit app.
"""

from .player import HumanPlayer
from .team import Team
from .tournament import Tournament


def build_sample_tournament(name="Elite Football League"):
    """Return a tournament with three teams and a few players registered."""
    tournament = Tournament(name)

    real_madrid = Team(1, "Real Madrid")
    barcelona = Team(2, "Barcelona")
    liverpool = Team(3, "Liverpool")

    real_madrid.add_player(HumanPlayer(101, "Player One", "Forward"))
    real_madrid.add_player(HumanPlayer(102, "Player Two", "Defender"))
    barcelona.add_player(HumanPlayer(201, "Player Three", "Goalkeeper"))
    liverpool.add_player(HumanPlayer(301, "Player Four", "Midfielder"))

    for team in (real_madrid, barcelona, liverpool):
        tournament.register_team(team)

    return tournament
