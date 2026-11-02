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
"""

from league import CardType, build_sample_tournament


def run_demo():
    # Create a tournament with teams and players already registered.
    tournament = build_sample_tournament("Elite Football League")

    # Generate the schedule and show the upcoming fixtures.
    tournament.generate_schedule()
    tournament.display_schedule()

    # Match 1: start, record a card, finish with the actual score.
    match1 = tournament.get_match(1)
    match1.start_match()

    player1 = tournament.find_player(101)
    match1.add_card(player1, CardType.YELLOW)

    match1.finish_match(3, 1)

    # Match 2: a draw.
    match2 = tournament.get_match(2)
    match2.start_match()
    match2.finish_match(0, 0)

    # Match 3: away win.
    match3 = tournament.get_match(3)
    match3.start_match()
    match3.finish_match(1, 2)

    # Final results.
    tournament.display_schedule()
    tournament.display_standings()

    print()
    print(match1.get_match_details())
    print(match1.get_result())
    print(player1.get_info())


if __name__ == "__main__":
    run_demo()
