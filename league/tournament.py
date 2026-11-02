"""
6. TOURNAMENT

Owns the registered teams and the generated fixtures, and computes
the league table from finished matches.
"""

from .constants import (
    MIN_TEAMS_FOR_SCHEDULE,
    MIN_TOURNAMENT_NAME_LENGTH,
    POINTS_FOR_DRAW,
    POINTS_FOR_WIN,
)
from .football_match import FootballMatch
from .player import HumanPlayer
from .team import Team


class Tournament:
    def __init__(self, name):
        if not self.validate_tournament_name(name):
            raise ValueError(
                "Tournament name must contain at least "
                f"{MIN_TOURNAMENT_NAME_LENGTH} characters."
            )

        self.name = name.strip()
        self.teams = []
        self.matches = []
        self.schedule_generated = False

    @staticmethod
    def validate_tournament_name(name):
        return (
            isinstance(name, str)
            and len(name.strip()) >= MIN_TOURNAMENT_NAME_LENGTH
        )

    # ------------------------------------------------------------------ #
    # Teams
    # ------------------------------------------------------------------ #
    def register_team(self, team):
        if self.schedule_generated:
            raise RuntimeError(
                "Cannot register teams after schedule generation."
            )

        if not isinstance(team, Team):
            raise TypeError("Only Team objects can be registered.")

        if self.get_team(team.id) is not None:
            raise ValueError("A team with this ID is already registered.")

        if any(t.name.casefold() == team.name.casefold() for t in self.teams):
            raise ValueError("A team with this name is already registered.")

        # A player cannot represent two clubs in the same tournament.
        for player in team.players:
            if self.find_player(player.id) is not None:
                raise ValueError(
                    f"Player ID {player.id!r} already plays for another "
                    "registered team."
                )

        self.teams.append(team)

    def unregister_team(self, team_id):
        if self.schedule_generated:
            raise RuntimeError(
                "Cannot remove teams after schedule generation."
            )

        team = self.get_team(team_id)

        if team is None:
            raise ValueError("Team was not found in this tournament.")

        self.teams.remove(team)
        return team

    def get_team(self, team_id):
        for team in self.teams:
            if team.id == team_id:
                return team

        return None

    def set_team_active(self, team_id, active):
        """Activate / deactivate a team, refusing while it has a live match."""
        team = self.get_team(team_id)

        if team is None:
            raise ValueError("Team was not found in this tournament.")

        if not active and any(
            m.is_live and m.involves(team) for m in self.matches
        ):
            raise RuntimeError(
                "Cannot deactivate a team while it is playing a live match."
            )

        if active:
            team.activate()
        else:
            team.deactivate()

        return team

    @property
    def active_teams(self):
        return [team for team in self.teams if team.is_active]

    # ------------------------------------------------------------------ #
    # Players (tournament-wide uniqueness)
    # ------------------------------------------------------------------ #
    def add_player_to_team(self, team_id, player):
        team = self.get_team(team_id)

        if team is None:
            raise ValueError("Team was not found in this tournament.")

        if not isinstance(player, HumanPlayer):
            raise TypeError("Only HumanPlayer objects can be added.")

        if self.find_player(player.id) is not None:
            raise ValueError(
                "A player with this ID already exists in the tournament."
            )

        team.add_player(player)
        return player

    def find_player(self, player_id):
        for team in self.teams:
            player = team.get_player(player_id)
            if player is not None:
                return player

        return None

    @property
    def all_players(self):
        return [player for team in self.teams for player in team.players]

    # ------------------------------------------------------------------ #
    # Fixtures
    # ------------------------------------------------------------------ #
    def generate_schedule(self):
        if self.schedule_generated:
            raise RuntimeError("Schedule has already been generated.")

        active_teams = self.active_teams

        if len(active_teams) < MIN_TEAMS_FOR_SCHEDULE:
            raise ValueError(
                f"At least {MIN_TEAMS_FOR_SCHEDULE} active teams are required."
            )

        match_id = 1

        # Single round-robin: every pair of active teams plays once.
        for i in range(len(active_teams)):
            for j in range(i + 1, len(active_teams)):
                self.matches.append(
                    FootballMatch(match_id, active_teams[i], active_teams[j])
                )
                match_id += 1

        self.schedule_generated = True
        return self.matches

    def get_match(self, match_id):
        for match in self.matches:
            if match.match_id == match_id:
                return match

        return None

    def get_matches_by_status(self, status):
        return [match for match in self.matches if match.status == status]

    @property
    def is_complete(self):
        return bool(self.matches) and all(m.is_finished for m in self.matches)

    # ------------------------------------------------------------------ #
    # Standings
    # ------------------------------------------------------------------ #
    def get_standings(self):
        table = {
            team.id: {
                "team": team,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
            }
            for team in self.teams
        }

        for match in self.matches:
            if not match.is_finished:
                continue

            score1, score2 = match.score

            t1 = table[match.team1.id]
            t2 = table[match.team2.id]

            t1["played"] += 1
            t2["played"] += 1

            t1["goals_for"] += score1
            t1["goals_against"] += score2

            t2["goals_for"] += score2
            t2["goals_against"] += score1

            if score1 > score2:
                t1["won"] += 1
                t2["lost"] += 1
                t1["points"] += POINTS_FOR_WIN

            elif score2 > score1:
                t2["won"] += 1
                t1["lost"] += 1
                t2["points"] += POINTS_FOR_WIN

            else:
                t1["drawn"] += 1
                t2["drawn"] += 1
                t1["points"] += POINTS_FOR_DRAW
                t2["points"] += POINTS_FOR_DRAW

        for row in table.values():
            row["goal_difference"] = row["goals_for"] - row["goals_against"]

        # Points, then goal difference, then goals scored (all descending);
        # team name ascending as a stable alphabetical tie-breaker.
        standings = sorted(
            table.values(),
            key=lambda row: (
                -row["points"],
                -row["goal_difference"],
                -row["goals_for"],
                row["team"].name.casefold(),
            ),
        )

        return [
            {"rank": index, **row}
            for index, row in enumerate(standings, start=1)
        ]

    # ------------------------------------------------------------------ #
    # Console output
    # ------------------------------------------------------------------ #
    def display_schedule(self):
        print(f"\n=== {self.name}: Match Schedule ===")

        for match in self.matches:
            if match.score is None:
                score = "Not played"
            else:
                score = f"{match.score[0]} - {match.score[1]}"

            print(
                f"Match {match.match_id}: "
                f"{match.team1.name} vs {match.team2.name} | "
                f"{score} | {match.status}"
            )

    def display_standings(self):
        standings = self.get_standings()

        print(f"\n=== {self.name}: Standings ===")
        print(
            f"{'Rank':<5} {'Team':<20} {'P':<3} "
            f"{'W':<3} {'D':<3} {'L':<3} "
            f"{'GF':<4} {'GA':<4} {'GD':<4} {'Pts':<4}"
        )
        print("-" * 65)

        for row in standings:
            print(
                f"{row['rank']:<5} "
                f"{row['team'].name:<20} "
                f"{row['played']:<3} "
                f"{row['won']:<3} "
                f"{row['drawn']:<3} "
                f"{row['lost']:<3} "
                f"{row['goals_for']:<4} "
                f"{row['goals_against']:<4} "
                f"{row['goal_difference']:<4} "
                f"{row['points']:<4}"
            )
