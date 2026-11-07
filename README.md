# Elite Arena — Football League Manager

An OOP football-league model (players, teams, matches, tournament) with a
Streamlit front end. All league rules live in the `league` package; the UI
only displays state and forwards actions to it.

## Features

- **Dashboard**: season hero (phase, progress, leader), the current matchday as scoreboards, KPI tiles, the league table with form, points and goal-difference charts, a position race across matchdays, latest results and the activity feed.
- **Fixtures & Results**: fixtures grouped by matchday with matchday / status filters, kick-off, yellow / red cards with the minute (two yellows = automatic send-off), final scores, and a match report with the match timeline.
- **Standings**: the official table (P, W, D, L, GF, GA, GD, PTS) with last-five form, goals scored vs conceded, goal difference, and a form guide (streak, unbeaten run, clean sheets, cards).
- **Teams & Players**: squads, player registration with a role, ban / unban / remove players, activate / deactivate teams, per-club season stats and club history.
- **History**: the full season timeline with filters and a table view, results by matchday, the table after any matchday with a position-race chart, and trends (goals per matchday, how matches ended, cards by team, discipline).
- **Tools**: CSV exports (standings, fixtures, players, cards, timeline), a JSON snapshot, a Markdown season report, result simulation (next matchday, whole season or a single match), head-to-head records and team comparison.
- **Manage League**: register or remove teams, generate a round-robin schedule (every team plays once per matchday), start a new tournament or load a sample league.
- **Clear feedback**: every invalid action (duplicate team, banned player, card outside a live match, ...) is rejected by the OOP model and shown as a message in the UI.
- **Images, icons and motion**: generated crests (initials + club colour) and avatars everywhere, with your own crest / player photo / stadium backdrop uploadable from the UI or dropped into `assets/` (see `assets/README.md`); Lucide and Material icons; a staggered page entrance, a live-match pulse, the progress meter filling, hover lifts, and balloons when the season is complete, all disabled under reduced-motion.

## Project layout

```
code/
├── main.py                 Console demo of the OOP model   -> python main.py
├── streamlit_app.py        Streamlit entry point           -> streamlit run streamlit_app.py
├── requirements.txt
│
├── .streamlit/config.toml  Theme (navy / gold) picked up by native widgets
├── assets/                 Your images: teams/<id>.png, players/<id>.png, hero.jpg
│
├── league/                 Domain model (no UI dependencies)
│   ├── constants.py        Statuses, results, phases, card types, roles, points rules
│   ├── validators.py       Shared input validation helpers
│   ├── events.py           Event / EventLog: the history of a tournament or match
│   ├── participant.py      Participant (ABC)
│   ├── player.py           HumanPlayer
│   ├── team.py             Team
│   ├── match.py            Match (ABC): lifecycle, timestamps, per-match events
│   ├── football_match.py   FootballMatch (cards with minutes, send-offs)
│   ├── tournament.py       Tournament (registration, matchdays, standings, timeline)
│   ├── analytics.py        Form, streaks, head-to-head, standings over time, summaries
│   ├── simulation.py       Play fixtures with random results (through the same rules)
│   ├── export.py           CSV rows, JSON snapshot, Markdown report
│   └── sample_data.py      build_sample_tournament()
│
├── ui/                     Streamlit presentation layer
│   ├── styles.py           Design tokens, CSS and motion
│   ├── icons.py            Inline Lucide icons + Material shortcodes for widgets
│   ├── assets.py           Crests, avatars and the hero backdrop (uploads, assets/, generated)
│   ├── charts.py           Altair chart builders (one shared theme)
│   ├── state.py            Session state, navigation, flash messages, run_action()
│   ├── components.py       Hero, scoreboards, stat tiles, table, timeline (HTML-escaped)
│   ├── helpers.py          Domain -> text / DataFrame converters
│   ├── sidebar.py          Navigation and season card
│   └── views/              One module per page
│       ├── dashboard.py
│       ├── fixtures.py
│       ├── standings.py
│       ├── teams.py
│       ├── history.py
│       ├── tools.py
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
| Schedule is a single round-robin over active teams (min. 2), grouped in matchdays where every team plays at most once | `Tournament.generate_schedule` |
| Match lifecycle: Upcoming → Live → Finished; both teams must be active to start | `Match` |
| Scores are non-negative integers | `Match.finish_match` |
| Cards only during live matches, only for participating, non-banned, not-yet-sent-off players; the minute, if given, is 1–120 | `FootballMatch.add_card` |
| Two yellow cards = automatic send-off (red) | `FootballMatch` |
| Every action is recorded with a timestamp (tournament history + per-match events) | `events.py`, `Tournament.get_timeline` |
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
