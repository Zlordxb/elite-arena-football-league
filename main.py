"""
Console demo of the OOP model (no Streamlit needed).

Run with:
    python main.py

The classes themselves live in the `league` package:
    league/participant.py      Participant (ABC)
    league/player.py           HumanPlayer
    league/team.py             Team
    league/match.py            Match (ABC)
    league/football_match.py   FootballMatch
    league/tournament.py       Tournament
    league/analytics.py        form, head-to-head, standings over time
"""

from league import CardType, analytics, build_sample_tournament


def run_demo():
    # Create a tournament with teams and players already registered.
    tournament = build_sample_tournament("Elite Football League")

    # Generate the schedule (grouped in matchdays) and show the fixtures.
    tournament.generate_schedule()
    tournament.display_schedule()

    # Match 1: kick off, book a player in the 34th minute, enter the score.
    tournament.start_match(1)
    tournament.record_card(1, 101, CardType.YELLOW, minute=34)
    tournament.finish_match(1, 3, 1)

    # Match 2: a draw.
    tournament.start_match(2)
    tournament.finish_match(2, 0, 0)

    # Match 3: away win.
    tournament.start_match(3)
    tournament.finish_match(3, 1, 2)

    # Final results, table and the season's timeline.
    tournament.display_schedule()
    tournament.display_standings()
    tournament.display_timeline()

    # A few of the analytics the dashboard is built on.
    real_madrid = tournament.get_team(1)
    form = analytics.team_form(tournament, real_madrid)
    print(f"\nReal Madrid form: {analytics.form_string(form)}")

    record = analytics.head_to_head(tournament, real_madrid, tournament.get_team(2))
    print(
        f"Head-to-head Real Madrid vs Barcelona: "
        f"{record['wins_a']} - {record['draws']} - {record['wins_b']}"
    )

    print()
    print(tournament.get_match(1).get_match_details())
    print(tournament.get_match(1).get_result())
    print(tournament.find_player(101).get_info())


if __name__ == "__main__":
    run_demo()
