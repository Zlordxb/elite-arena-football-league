"""
6. TOURNAMENT

Owns the registered teams, the generated fixtures (grouped in matchdays),
the league table and the tournament history.

The *_match / *_player methods are thin facades: they look the object up
by ID and delegate to it, so the UI never has to hold object references.
"""

from datetime import datetime

from .constants import (
    MIN_TEAMS_FOR_SCHEDULE,
    MIN_TOURNAMENT_NAME_LENGTH,
    POINTS_FOR_DRAW,
    POINTS_FOR_WIN,
    SeasonPhase,
)
from .events import EventLog, EventType
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

        # History
        self.created_at = datetime.now()
        self.history = EventLog()

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
        self.history.record(
            EventType.TEAM_REGISTERED,
            f"{team.name} joined the tournament.",
            team_id=team.id, team=team.name,
        )

    def unregister_team(self, team_id):
        if self.schedule_generated:
            raise RuntimeError(
                "Cannot remove teams after schedule generation."
            )

        team = self._require_team(team_id)
        self.teams.remove(team)
        self.history.record(
            EventType.TEAM_REMOVED,
            f"{team.name} left the tournament.",
            team_id=team.id, team=team.name,
        )
        return team

    def get_team(self, team_id):
        for team in self.teams:
            if team.id == team_id:
                return team

        return None

    def _require_team(self, team_id):
        team = self.get_team(team_id)

        if team is None:
            raise ValueError("Team was not found in this tournament.")

        return team

    def set_team_active(self, team_id, active):
        """Activate / deactivate a team, refusing while it has a live match."""
        team = self._require_team(team_id)

        if not active and any(
            m.is_live and m.involves(team) for m in self.matches
        ):
            raise RuntimeError(
                "Cannot deactivate a team while it is playing a live match."
            )

        if active:
            team.activate()
            self.history.record(
                EventType.TEAM_ACTIVATED,
                f"{team.name} is active again.",
                team_id=team.id, team=team.name,
            )
        else:
            team.deactivate()
            self.history.record(
                EventType.TEAM_DEACTIVATED,
                f"{team.name} was deactivated.",
                team_id=team.id, team=team.name,
            )

        return team

    @property
    def active_teams(self):
        return [team for team in self.teams if team.is_active]

    # ------------------------------------------------------------------ #
    # Players (tournament-wide uniqueness)
    # ------------------------------------------------------------------ #
    def add_player_to_team(self, team_id, player):
        team = self._require_team(team_id)

        if not isinstance(player, HumanPlayer):
            raise TypeError("Only HumanPlayer objects can be added.")

        if self.find_player(player.id) is not None:
            raise ValueError(
                "A player with this ID already exists in the tournament."
            )

        team.add_player(player)
        self.history.record(
            EventType.PLAYER_ADDED,
            f"{player.name} ({player.role}) joined {team.name}.",
            player_id=player.id, player=player.name, team=team.name,
        )
        return player

    def remove_player(self, player_id):
        player = self._require_player(player_id)
        team = player.team

        team.remove_player(player_id)
        self.history.record(
            EventType.PLAYER_REMOVED,
            f"{player.name} left {team.name}.",
            player_id=player.id, player=player.name, team=team.name,
        )
        return player

    def ban_player(self, player_id):
        player = self._require_player(player_id)
        player.ban()
        self.history.record(
            EventType.PLAYER_BANNED,
            f"{player.name} ({player.team.name}) was banned.",
            player_id=player.id, player=player.name, team=player.team.name,
        )
        return player

    def unban_player(self, player_id):
        player = self._require_player(player_id)
        player.unban()
        self.history.record(
            EventType.PLAYER_UNBANNED,
            f"{player.name} ({player.team.name}) is available again.",
            player_id=player.id, player=player.name, team=player.team.name,
        )
        return player

    def find_player(self, player_id):
        for team in self.teams:
            player = team.get_player(player_id)
            if player is not None:
                return player

        return None

    def _require_player(self, player_id):
        player = self.find_player(player_id)

        if player is None:
            raise ValueError("Player was not found in this tournament.")

        return player

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

        # Single round-robin, grouped in matchdays: every pair of active
        # teams plays once, and every team plays at most once per matchday.
        match_id = 1

        for matchday, pairs in enumerate(self._round_robin_rounds(active_teams), start=1):
            for home, away in pairs:
                match = FootballMatch(match_id, home, away)
                match.matchday = matchday
                self.matches.append(match)
                match_id += 1

        self.schedule_generated = True
        self.history.record(
            EventType.SCHEDULE_GENERATED,
            f"Schedule generated: {len(self.matches)} matches over "
            f"{self.total_matchdays} matchdays.",
            matches=len(self.matches), matchdays=self.total_matchdays,
        )
        return self.matches

    @staticmethod
    def _round_robin_rounds(teams):
        """
        Circle method. Returns a list of matchdays; each matchday is a list
        of (home, away) pairs in which every team appears at most once.
        With an odd number of teams one team rests each matchday.
        """
        slots = list(teams)
        if len(slots) % 2:
            slots.append(None)  # bye

        count = len(slots)
        fixed, rotating = slots[-1], slots[:-1]
        order = {id(team): index for index, team in enumerate(teams)}
        rounds = []

        for _ in range(count - 1):
            ring = [fixed] + rotating
            pairs = []

            for i in range(count // 2):
                a, b = ring[i], ring[count - 1 - i]

                if a is None or b is None:
                    continue

                # The earlier-registered team is listed first ("home").
                if order[id(a)] > order[id(b)]:
                    a, b = b, a

                pairs.append((a, b))

            pairs.sort(key=lambda pair: order[id(pair[0])])
            rounds.append(pairs)
            rotating = [rotating[-1]] + rotating[:-1]

        return rounds

    def get_match(self, match_id):
        for match in self.matches:
            if match.match_id == match_id:
                return match

        return None

    def _require_match(self, match_id):
        match = self.get_match(match_id)

        if match is None:
            raise ValueError("Match was not found in this tournament.")

        return match

    def start_match(self, match_id):
        match = self._require_match(match_id)
        match.start_match()
        return match

    def finish_match(self, match_id, team1_score, team2_score):
        match = self._require_match(match_id)
        match.finish_match(team1_score, team2_score)
        return match

    def record_card(self, match_id, player_id, card_type, minute=None):
        match = self._require_match(match_id)
        player = self._require_player(player_id)
        return match.add_card(player, card_type, minute)

    def get_matches_by_status(self, status):
        return [match for match in self.matches if match.status == status]

    @property
    def matchdays(self):
        """{matchday: [matches]} in matchday order."""
        grouped = {}

        for match in self.matches:
            grouped.setdefault(match.matchday, []).append(match)

        return dict(sorted(grouped.items()))

    @property
    def total_matchdays(self):
        return max((m.matchday for m in self.matches), default=0)

    @property
    def current_matchday(self):
        """First matchday that still has an unfinished match (None if done)."""
        for matchday, matches in self.matchdays.items():
            if not all(m.is_finished for m in matches):
                return matchday

        return None

    @property
    def finished_matches(self):
        """Finished matches in the order they were completed."""
        return sorted(
            (m for m in self.matches if m.is_finished),
            key=lambda m: (m.finished_at, str(m.match_id)),
        )

    @property
    def is_complete(self):
        return bool(self.matches) and all(m.is_finished for m in self.matches)

    @property
    def phase(self):
        if not self.schedule_generated:
            if len(self.active_teams) < MIN_TEAMS_FOR_SCHEDULE:
                return SeasonPhase.SETUP
            return SeasonPhase.READY

        if self.is_complete:
            return SeasonPhase.COMPLETE

        return SeasonPhase.IN_PROGRESS

    # ------------------------------------------------------------------ #
    # Standings
    # ------------------------------------------------------------------ #
    def get_standings(self, matches=None):
        """
        League table built from finished matches.
        Pass `matches` to build the table from a subset (used for history).
        """
        if matches is None:
            matches = self.matches

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

        for match in matches:
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

    def get_standings_after_matchday(self, matchday):
        """The table as it stood once matchday `matchday` had been played."""
        return self.get_standings(
            matches=[m for m in self.matches if m.matchday <= matchday]
        )

    # ------------------------------------------------------------------ #
    # History
    # ------------------------------------------------------------------ #
    def get_timeline(self, newest_first=True):
        """Tournament events merged with every match's events."""
        events = list(self.history)

        for match in self.matches:
            events.extend(match.events)

        events.sort(key=lambda e: e.sort_key, reverse=newest_first)
        return events

    # ------------------------------------------------------------------ #
    # Console output
    # ------------------------------------------------------------------ #
    def display_schedule(self):
        print(f"\n=== {self.name}: Match Schedule ===")

        for matchday, matches in self.matchdays.items():
            print(f"-- Matchday {matchday} --")

            for match in matches:
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

    def display_timeline(self, limit=20):
        print(f"\n=== {self.name}: Timeline ===")

        for event in self.get_timeline(newest_first=False)[-limit:]:
            stamp = event.timestamp.strftime("%H:%M:%S")
            print(f"{stamp}  {event.label:<18} {event.message}")
