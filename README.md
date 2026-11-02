# Elite Arena — Football League Manager

An OOP football-league model (players, teams, matches, tournament) with a
Streamlit front end. All league rules live in the `league` package; the UI
only displays state and forwards actions to it.

## Features

- **Dashboard**: season overview cards, recent results, season progress and the current league table.
- **Fixtures & Results**: filter matches by status, start a match, record yellow / red cards (two yellows = automatic send-off) and save the final score.
- **Standings**: the official table (P, W, D, L, GF, GA, GD, PTS), recalculated after every result, with a champion banner when the season is complete.
- **Teams & Players**: browse squads, add players with a role, ban / unban or remove players, and activate / deactivate teams.
- **Manage League**: register or remove teams, generate a round-robin schedule, start a new tournament or load a sample league.
- **Clear feedback**: every invalid action (duplicate team, banned player, card outside a live match, ...) is rejected by the OOP model and shown as a message in the UI.

## Project layout

```
code/
├── main.py                 Console demo of the OOP model   -> python main.py
├── streamlit_app.py        Streamlit entry point           -> streamlit run streamlit_app.py
├── requirements.txt
│
├── league/                 Domain model (no UI dependencies)
│   ├── constants.py        Statuses, card types, roles, points rules
│   ├── validators.py       Shared input validation helpers
│   ├── participant.py      Participant (ABC)
│   ├── player.py           HumanPlayer
│   ├── team.py             Team
│   ├── match.py            Match (ABC)
│   ├── football_match.py   FootballMatch (cards, send-offs)
│   ├── tournament.py       Tournament (registration, schedule, standings)
│   └── sample_data.py      build_sample_tournament()
│
├── ui/                     Streamlit presentation layer
│   ├── styles.py           Theme CSS
│   ├── state.py            Session state, flash messages, run_action()
│   ├── components.py       Header, cards, pills (HTML-escaped)
│   ├── helpers.py          Domain -> DataFrame converters
│   ├── sidebar.py          Navigation
│   └── views/              One module per page
│       ├── dashboard.py
│       ├── fixtures.py
│       ├── standings.py
│       ├── teams.py
│       └── manage.py
│
└── tests/
    └── test_league.py      Unit tests for the domain  -> python -m unittest -v
```

## Class hierarchy

```
Participant (ABC)            Match (ABC)
├── HumanPlayer              └── FootballMatch
└── Team
                             Tournament
```

## Running

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py     # web app
python main.py                     # console demo
python -m unittest -v              # tests
```

## League rules enforced by the model

| Rule | Where |
|------|-------|
| IDs and names must be non-empty; strings are trimmed | `validators.py` |
| Player role must be Goalkeeper / Defender / Midfielder / Forward | `HumanPlayer` |
| A player belongs to at most one team, and IDs are unique per tournament | `Team.add_player`, `Tournament.add_player_to_team` |
| Team IDs and names (case-insensitive) are unique per tournament | `Tournament.register_team` |
| Teams can be registered or removed only before the schedule exists | `Tournament` |
| Schedule is a single round-robin over active teams (min. 2) | `Tournament.generate_schedule` |
| Match lifecycle: Upcoming → Live → Finished; both teams must be active to start | `Match` |
| Scores are non-negative integers | `Match.finish_match` |
| Cards only during live matches, only for participating, non-banned, not-yet-sent-off players | `FootballMatch.add_card` |
| Two yellow cards = automatic send-off (red) | `FootballMatch` |
| A team cannot be deactivated while it has a live match | `Tournament.set_team_active` |
| Standings: 3 points for a win, 1 for a draw; ranked by points, goal difference, goals for, then name | `Tournament.get_standings` |

## Team

| Member | Contribution |
|--------|--------------|
| [Taha Mohamed](https://www.linkedin.com/in/taha-mohamed-bb71b328a/) | Streamlit GUI (`streamlit_app.py`, `ui/`) |
| [Ahmed Ayman](https://www.linkedin.com/in/ahmed-ayman-777850389) | OOP domain model (`league/`) |

## Acknowledgments

Built as a team project during our training at
[Instant Software Solutions](https://www.linkedin.com/company/instantsoftwaresolution/),
under the guidance of Eng. Gad.
