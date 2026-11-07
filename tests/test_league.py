"""
Unit tests for the league domain.

Run with:
    python -m unittest -v
"""

import json
import random
import unittest

from league import (
    CardType,
    EventLog,
    EventType,
    FootballMatch,
    HumanPlayer,
    MatchResult,
    MatchStatus,
    SeasonPhase,
    SendOffReason,
    Team,
    Tournament,
    analytics,
    build_sample_tournament,
    export,
    simulation,
)


def make_player(pid=1, name="Player", role="Forward"):
    return HumanPlayer(pid, name, role)


def make_team(tid=1, name="Team", players=0):
    team = Team(tid, name)
    for i in range(players):
        team.add_player(make_player(tid * 100 + i, f"{name} {i}"))
    return team


def make_live_match(players_per_team=2):
    t1 = make_team(1, "Alpha", players_per_team)
    t2 = make_team(2, "Beta", players_per_team)
    match = FootballMatch(1, t1, t2)
    match.start_match()
    return match, t1, t2


def make_league(team_count, players=2):
    tournament = Tournament("Test League")
    for i in range(1, team_count + 1):
        tournament.register_team(make_team(i, f"Team {i}", players))
    return tournament


def play(tournament, match_id, score):
    tournament.start_match(match_id)
    tournament.finish_match(match_id, *score)


# ---------------------------------------------------------------------- #
# Participant / HumanPlayer
# ---------------------------------------------------------------------- #
class HumanPlayerTests(unittest.TestCase):
    def test_valid_player_normalises_inputs(self):
        player = HumanPlayer(" 7 ", "  Mo Salah ", "forward")
        self.assertEqual(player.id, "7")
        self.assertEqual(player.name, "Mo Salah")
        self.assertEqual(player.role, "Forward")
        self.assertFalse(player.is_banned)
        self.assertIsNone(player.team)

    def test_invalid_ids(self):
        for bad in (None, "", "   ", True, 1.5, []):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    HumanPlayer(bad, "Name", "Forward")

    def test_invalid_names(self):
        for bad in (None, "", "   ", 5):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    HumanPlayer(1, bad, "Forward")

    def test_invalid_roles(self):
        for bad in (None, "", "Coach", 3):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    HumanPlayer(1, "Name", bad)

    def test_ban_and_unban(self):
        player = make_player()
        player.ban()
        self.assertTrue(player.is_banned)
        self.assertFalse(player.is_available)

        with self.assertRaises(ValueError):
            player.ban()

        player.unban()
        self.assertFalse(player.is_banned)

        with self.assertRaises(ValueError):
            player.unban()

    def test_get_info(self):
        player = make_player(9, "Nine", "Defender")
        self.assertEqual(
            player.get_info(),
            {"id": 9, "name": "Nine", "role": "Defender",
             "is_banned": False, "team": None},
        )


# ---------------------------------------------------------------------- #
# Team
# ---------------------------------------------------------------------- #
class TeamTests(unittest.TestCase):
    def test_add_player_sets_back_reference(self):
        team = make_team()
        player = make_player()
        team.add_player(player)
        self.assertIs(player.team, team)
        self.assertIs(team.get_player(1), player)
        self.assertTrue(team.has_player(1))

    def test_only_human_players_can_join(self):
        with self.assertRaises(TypeError):
            make_team().add_player("not a player")

    def test_duplicate_player_id_rejected(self):
        team = make_team()
        team.add_player(make_player(1))
        with self.assertRaises(ValueError):
            team.add_player(make_player(1))

    def test_player_cannot_join_two_teams(self):
        player = make_player()
        make_team(1, "A").add_player(player)
        with self.assertRaises(ValueError):
            make_team(2, "B").add_player(player)

    def test_remove_player_clears_back_reference(self):
        team = make_team()
        player = make_player()
        team.add_player(player)
        removed = team.remove_player(1)
        self.assertIs(removed, player)
        self.assertIsNone(player.team)
        self.assertEqual(team.players, [])

        with self.assertRaises(ValueError):
            team.remove_player(1)

    def test_activate_deactivate(self):
        team = make_team()
        with self.assertRaises(ValueError):
            team.activate()
        team.deactivate()
        self.assertFalse(team.is_active)
        with self.assertRaises(ValueError):
            team.deactivate()
        team.activate()
        self.assertTrue(team.is_active)

    def test_available_and_banned_players(self):
        team = make_team(players=3)
        team.players[0].ban()
        self.assertEqual(len(team.available_players), 2)
        self.assertEqual(len(team.banned_players), 1)
        self.assertEqual(team.get_info()["banned_count"], 1)


# ---------------------------------------------------------------------- #
# Match / FootballMatch
# ---------------------------------------------------------------------- #
class MatchTests(unittest.TestCase):
    def test_requires_two_distinct_teams(self):
        team = make_team()
        with self.assertRaises(TypeError):
            FootballMatch(1, team, "Beta")
        with self.assertRaises(ValueError):
            FootballMatch(1, team, team)
        with self.assertRaises(ValueError):
            FootballMatch(1, make_team(1, "A"), make_team(1, "B"))

    def test_match_id_validated(self):
        with self.assertRaises(ValueError):
            FootballMatch("", make_team(1, "A"), make_team(2, "B"))

    def test_lifecycle(self):
        match = FootballMatch(1, make_team(1, "A"), make_team(2, "B"))
        self.assertTrue(match.is_upcoming)
        self.assertIsNone(match.get_result())
        self.assertIsNone(match.started_at)

        with self.assertRaises(RuntimeError):
            match.finish_match(1, 0)

        match.start_match()
        self.assertTrue(match.is_live)
        self.assertIsNotNone(match.started_at)

        with self.assertRaises(RuntimeError):
            match.start_match()

        match.finish_match(2, 1)
        self.assertTrue(match.is_finished)
        self.assertIsNotNone(match.finished_at)
        self.assertEqual(match.score, (2, 1))
        self.assertEqual(match.get_result()["winner"], "A")

        with self.assertRaises(RuntimeError):
            match.finish_match(0, 0)

    def test_match_events(self):
        match, _, _ = make_live_match()
        match.finish_match(1, 1)
        types = [e.type for e in match.events]
        self.assertEqual(types, [EventType.MATCH_STARTED, EventType.MATCH_FINISHED])
        self.assertIn("1 - 1", match.events.events[-1].message)

    def test_inactive_team_cannot_start(self):
        t1, t2 = make_team(1, "A"), make_team(2, "B")
        t2.deactivate()
        match = FootballMatch(1, t1, t2)
        with self.assertRaises(RuntimeError):
            match.start_match()

    def test_invalid_scores(self):
        match, _, _ = make_live_match()
        for bad in ((-1, 0), (1.5, 0), ("1", 0), (True, 0), (None, 0)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    match.finish_match(*bad)
        self.assertTrue(match.is_live)

    def test_draw_has_no_winner(self):
        match, _, _ = make_live_match()
        match.finish_match(1, 1)
        self.assertIsNone(match.winner)
        self.assertEqual(match.get_result()["winner"], "Draw")

    def test_per_team_queries(self):
        match, t1, t2 = make_live_match()
        self.assertIsNone(match.result_for(t1))
        match.finish_match(3, 1)

        self.assertEqual(match.result_for(t1), MatchResult.WIN)
        self.assertEqual(match.result_for(t2), MatchResult.LOSS)
        self.assertEqual((match.goals_for(t2), match.goals_against(t2)), (1, 3))
        self.assertIs(match.opponent_of(t1), t2)
        self.assertEqual(match.total_goals, 4)

        with self.assertRaises(ValueError):
            match.result_for(make_team(9, "Stranger"))


class FootballMatchCardTests(unittest.TestCase):
    def test_cards_only_during_live(self):
        match = FootballMatch(1, make_team(1, "A", 1), make_team(2, "B", 1))
        with self.assertRaises(RuntimeError):
            match.add_card(match.team1.players[0], CardType.YELLOW)

    def test_invalid_card_inputs(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]

        with self.assertRaises(ValueError):
            match.add_card(player, "blue")
        with self.assertRaises(ValueError):
            match.add_card(player, None)
        with self.assertRaises(TypeError):
            match.add_card("player", CardType.YELLOW)
        with self.assertRaises(ValueError):
            match.add_card(make_player(999, "Stranger"), CardType.YELLOW)

        self.assertEqual(match.yellow_cards, [])
        self.assertEqual(match.cards, [])

    def test_invalid_minutes(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]
        for bad in (0, 121, -5, 1.5, "45", True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    match.add_card(player, CardType.YELLOW, minute=bad)
        self.assertEqual(match.cards, [])

    def test_banned_player_cannot_receive_card(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]
        player.ban()
        with self.assertRaises(ValueError):
            match.add_card(player, CardType.YELLOW)

    def test_two_yellows_send_off(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]

        record = match.add_card(player, "Yellow", minute=12)
        self.assertEqual(record["minute"], 12)
        self.assertEqual(match.yellow_cards_for(player), 1)
        self.assertFalse(match.is_sent_off(player))

        match.add_card(player, "yellow", minute=70)
        self.assertTrue(match.is_sent_off(player))
        self.assertEqual(match.red_cards[0]["reason"], SendOffReason.SECOND_YELLOW)

        with self.assertRaises(ValueError):
            match.add_card(player, CardType.YELLOW)

        details = match.get_match_details()
        self.assertEqual(details["yellow_cards"], 2)
        self.assertEqual(details["red_cards"], 1)
        self.assertEqual(details["sent_off_players"], [player.id])

        types = [e.type for e in match.events]
        self.assertEqual(
            types,
            [EventType.MATCH_STARTED, EventType.CARD, EventType.CARD,
             EventType.CARD, EventType.SEND_OFF],
        )
        self.assertIn("70'", match.events.events[-1].message)

    def test_direct_red(self):
        match, _, t2 = make_live_match()
        player = t2.players[1]
        match.add_card(player, CardType.RED)
        self.assertTrue(match.is_sent_off(player))
        self.assertEqual(match.red_cards[0]["reason"], SendOffReason.DIRECT_RED)

        report = match.get_cards_report()
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["team"], "Beta")
        self.assertEqual(report[0]["card"], CardType.RED)
        self.assertIsNone(report[0]["minute"])
        self.assertEqual(len(match.cards_for_team(t2)), 1)
        self.assertEqual(len(match.cards_for_team(match.team1)), 0)


# ---------------------------------------------------------------------- #
# Events
# ---------------------------------------------------------------------- #
class EventLogTests(unittest.TestCase):
    def test_record_and_query(self):
        log = EventLog()
        first = log.record(EventType.TEAM_REGISTERED, "Alpha joined.", team="Alpha")
        second = log.record(EventType.PLAYER_BANNED, "Bob banned.")

        self.assertEqual(len(log), 2)
        self.assertEqual(log.latest(1), [second])
        self.assertEqual(log.of_type(EventType.TEAM_REGISTERED), [first])
        self.assertEqual(first.label, "Team registered")
        self.assertEqual(first.to_dict()["team"], "Alpha")
        self.assertLess(first.sort_key, second.sort_key)

    def test_invalid_events(self):
        log = EventLog()
        with self.assertRaises(ValueError):
            log.record("made_up", "x")
        with self.assertRaises(ValueError):
            log.record(EventType.CARD, "   ")


# ---------------------------------------------------------------------- #
# Tournament
# ---------------------------------------------------------------------- #
class TournamentTests(unittest.TestCase):
    def test_name_validation(self):
        for bad in (None, "", "ab", "  a  ", 5):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    Tournament(bad)
        self.assertEqual(Tournament("  Cup ").name, "Cup")

    def test_register_team_rules(self):
        tournament = Tournament("League")
        tournament.register_team(make_team(1, "Alpha"))

        with self.assertRaises(TypeError):
            tournament.register_team("Alpha")
        with self.assertRaises(ValueError):
            tournament.register_team(make_team(1, "Other"))
        with self.assertRaises(ValueError):
            tournament.register_team(make_team(2, "alpha"))

        self.assertEqual(tournament.history.events[0].type, EventType.TEAM_REGISTERED)

    def test_player_unique_across_teams(self):
        tournament = Tournament("League")
        tournament.register_team(make_team(1, "Alpha", 1))  # player 100

        clash = make_team(2, "Beta")
        clash.add_player(make_player(100, "Clash"))
        with self.assertRaises(ValueError):
            tournament.register_team(clash)

        tournament.register_team(make_team(3, "Gamma"))
        with self.assertRaises(ValueError):
            tournament.add_player_to_team(3, make_player(100, "Clash"))
        with self.assertRaises(ValueError):
            tournament.add_player_to_team(99, make_player(5, "Nobody"))
        with self.assertRaises(TypeError):
            tournament.add_player_to_team(3, "player")

        player = tournament.add_player_to_team(3, make_player(5, "New"))
        self.assertIs(tournament.find_player(5), player)
        self.assertEqual(len(tournament.all_players), 2)

    def test_player_facade_logs_history(self):
        tournament = make_league(2, players=1)
        tournament.ban_player(100)
        self.assertTrue(tournament.find_player(100).is_banned)
        tournament.unban_player(100)
        self.assertFalse(tournament.find_player(100).is_banned)
        tournament.remove_player(100)
        self.assertIsNone(tournament.find_player(100))

        with self.assertRaises(ValueError):
            tournament.ban_player(100)

        types = [e.type for e in tournament.history]
        self.assertEqual(
            types[-3:],
            [EventType.PLAYER_BANNED, EventType.PLAYER_UNBANNED, EventType.PLAYER_REMOVED],
        )

    def test_unregister_team(self):
        tournament = Tournament("League")
        tournament.register_team(make_team(1, "Alpha"))
        tournament.unregister_team(1)
        self.assertEqual(tournament.teams, [])
        with self.assertRaises(ValueError):
            tournament.unregister_team(1)

    def test_schedule_requires_two_active_teams(self):
        tournament = Tournament("League")
        tournament.register_team(make_team(1, "Alpha"))
        self.assertEqual(tournament.phase, SeasonPhase.SETUP)
        with self.assertRaises(ValueError):
            tournament.generate_schedule()

        beta = make_team(2, "Beta")
        beta.deactivate()
        tournament.register_team(beta)
        with self.assertRaises(ValueError):
            tournament.generate_schedule()

    def test_round_robin_schedule(self):
        tournament = build_sample_tournament()
        self.assertEqual(tournament.phase, SeasonPhase.READY)
        matches = tournament.generate_schedule()

        self.assertEqual(len(matches), 3)
        self.assertEqual([m.match_id for m in matches], [1, 2, 3])
        self.assertEqual([m.matchday for m in matches], [1, 2, 3])
        self.assertTrue(tournament.schedule_generated)
        self.assertEqual(tournament.phase, SeasonPhase.IN_PROGRESS)
        self.assertEqual(tournament.current_matchday, 1)

        with self.assertRaises(RuntimeError):
            tournament.generate_schedule()
        with self.assertRaises(RuntimeError):
            tournament.register_team(make_team(9, "Late"))
        with self.assertRaises(RuntimeError):
            tournament.unregister_team(1)

    def test_matchdays_are_valid_for_any_team_count(self):
        for count in range(2, 9):
            with self.subTest(teams=count):
                tournament = make_league(count, players=0)
                tournament.generate_schedule()

                expected_rounds = count - 1 if count % 2 == 0 else count
                self.assertEqual(tournament.total_matchdays, expected_rounds)
                self.assertEqual(len(tournament.matches), count * (count - 1) // 2)

                pairs = set()
                for matches in tournament.matchdays.values():
                    seen = set()
                    for m in matches:
                        self.assertNotIn(m.team1.id, seen)
                        self.assertNotIn(m.team2.id, seen)
                        seen.update((m.team1.id, m.team2.id))
                        pairs.add(frozenset((m.team1.id, m.team2.id)))
                self.assertEqual(len(pairs), len(tournament.matches))

    def test_match_facade(self):
        tournament = make_league(2, players=1)
        tournament.generate_schedule()

        with self.assertRaises(ValueError):
            tournament.start_match(99)

        match = tournament.start_match(1)
        self.assertTrue(match.is_live)

        record = tournament.record_card(1, 100, CardType.YELLOW, 33)
        self.assertEqual(record["minute"], 33)
        with self.assertRaises(ValueError):
            tournament.record_card(1, 999, CardType.YELLOW)

        tournament.finish_match(1, 1, 0)
        self.assertTrue(tournament.is_complete)
        self.assertEqual(tournament.phase, SeasonPhase.COMPLETE)
        self.assertIsNone(tournament.current_matchday)

    def test_cannot_deactivate_team_in_live_match(self):
        tournament = build_sample_tournament()
        tournament.generate_schedule()
        tournament.get_match(1).start_match()

        with self.assertRaises(RuntimeError):
            tournament.set_team_active(1, False)
        with self.assertRaises(ValueError):
            tournament.set_team_active(99, False)

        tournament.set_team_active(3, False)
        self.assertFalse(tournament.get_team(3).is_active)
        self.assertEqual(len(tournament.active_teams), 2)
        self.assertEqual(tournament.history.events[-1].type, EventType.TEAM_DEACTIVATED)

    def test_standings(self):
        tournament = build_sample_tournament()
        tournament.generate_schedule()

        # 1: Real Madrid 3-1 Barcelona, 2: Real Madrid 0-0 Liverpool,
        # 3: Barcelona 1-2 Liverpool
        for match_id, score in ((1, (3, 1)), (2, (0, 0)), (3, (1, 2))):
            play(tournament, match_id, score)

        self.assertTrue(tournament.is_complete)

        standings = tournament.get_standings()
        names = [row["team"].name for row in standings]
        self.assertEqual(names, ["Real Madrid", "Liverpool", "Barcelona"])
        self.assertEqual([row["rank"] for row in standings], [1, 2, 3])

        real = standings[0]
        self.assertEqual(
            (real["played"], real["won"], real["drawn"], real["lost"]),
            (2, 1, 1, 0),
        )
        self.assertEqual((real["goals_for"], real["goals_against"]), (3, 1))
        self.assertEqual(real["goal_difference"], 2)
        self.assertEqual(real["points"], 4)

        barca = standings[2]
        self.assertEqual(barca["points"], 0)
        self.assertEqual(barca["goal_difference"], -3)

    def test_standings_after_matchday(self):
        tournament = build_sample_tournament()
        tournament.generate_schedule()
        play(tournament, 1, (3, 1))          # matchday 1
        play(tournament, 2, (0, 0))          # matchday 2

        after_1 = tournament.get_standings_after_matchday(1)
        self.assertEqual(after_1[0]["team"].name, "Real Madrid")
        self.assertEqual(after_1[0]["points"], 3)
        self.assertEqual(after_1[1]["played"], 0)  # Liverpool has not played yet

        after_2 = tournament.get_standings_after_matchday(2)
        self.assertEqual(after_2[0]["points"], 4)

        baseline = tournament.get_standings_after_matchday(0)
        self.assertTrue(all(row["played"] == 0 for row in baseline))

    def test_standings_tie_breakers(self):
        tournament = Tournament("Tie")
        for tid, name in ((1, "Zeta"), (2, "Alpha"), (3, "Mid")):
            tournament.register_team(make_team(tid, name))
        tournament.generate_schedule()

        # Every match is a draw: same points, GD and GF -> alphabetical.
        for match in tournament.matches:
            match.start_match()
            match.finish_match(1, 1)

        names = [row["team"].name for row in tournament.get_standings()]
        self.assertEqual(names, ["Alpha", "Mid", "Zeta"])

    def test_matches_by_status(self):
        tournament = build_sample_tournament()
        tournament.generate_schedule()
        tournament.get_match(1).start_match()

        self.assertEqual(len(tournament.get_matches_by_status(MatchStatus.LIVE)), 1)
        self.assertEqual(len(tournament.get_matches_by_status(MatchStatus.UPCOMING)), 2)
        self.assertFalse(tournament.is_complete)

    def test_timeline_merges_tournament_and_match_events(self):
        tournament = make_league(2, players=1)
        tournament.generate_schedule()
        play(tournament, 1, (2, 0))

        oldest_first = tournament.get_timeline(newest_first=False)
        types = [e.type for e in oldest_first]
        self.assertEqual(
            types,
            [EventType.TEAM_REGISTERED, EventType.TEAM_REGISTERED,
             EventType.SCHEDULE_GENERATED, EventType.MATCH_STARTED,
             EventType.MATCH_FINISHED],
        )
        self.assertEqual(tournament.get_timeline()[0].type, EventType.MATCH_FINISHED)


# ---------------------------------------------------------------------- #
# Analytics
# ---------------------------------------------------------------------- #
class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.tournament = build_sample_tournament()
        self.tournament.generate_schedule()
        play(self.tournament, 1, (3, 1))   # Real Madrid 3-1 Barcelona
        play(self.tournament, 2, (0, 0))   # Real Madrid 0-0 Liverpool
        play(self.tournament, 3, (1, 2))   # Barcelona 1-2 Liverpool
        self.real = self.tournament.get_team(1)
        self.barca = self.tournament.get_team(2)
        self.liverpool = self.tournament.get_team(3)

    def test_form_and_streaks(self):
        form = analytics.team_form(self.tournament, self.real)
        self.assertEqual(analytics.form_string(form), "WD")
        self.assertEqual(form[0]["opponent"], self.barca)
        self.assertTrue(form[0]["home"])
        self.assertEqual(analytics.current_streak(form), ("D", 1))
        self.assertEqual(analytics.unbeaten_run(form), 2)

        barca_form = analytics.team_form(self.tournament, self.barca)
        self.assertEqual(analytics.form_string(barca_form), "LL")
        self.assertEqual(analytics.current_streak(barca_form), ("L", 2))
        self.assertEqual(analytics.unbeaten_run(barca_form), 0)
        self.assertIsNone(analytics.current_streak([]))

    def test_head_to_head(self):
        record = analytics.head_to_head(self.tournament, self.real, self.barca)
        self.assertEqual((record["wins_a"], record["draws"], record["wins_b"]), (1, 0, 0))
        self.assertEqual((record["goals_a"], record["goals_b"]), (3, 1))
        self.assertEqual(record["played"], 1)

        with self.assertRaises(ValueError):
            analytics.head_to_head(self.tournament, self.real, self.real)

    def test_standings_history(self):
        snapshots = analytics.standings_by_matchday(self.tournament)
        self.assertEqual([s["matchday"] for s in snapshots], [0, 1, 2, 3])
        self.assertEqual(snapshots[1]["standings"][0]["team"], self.real)
        self.assertEqual(snapshots[3]["standings"][1]["team"], self.liverpool)

        rows = analytics.position_history_rows(self.tournament)
        self.assertEqual(len(rows), 4 * 3)
        self.assertEqual({r["matchday"] for r in rows}, {0, 1, 2, 3})

    def test_summary_and_breakdown(self):
        summary = analytics.season_summary(self.tournament)
        self.assertEqual(summary["played"], 3)
        self.assertEqual(summary["goals"], 7)
        self.assertEqual(summary["goals_per_match"], 2.33)
        self.assertEqual((summary["home_wins"], summary["draws"], summary["away_wins"]), (1, 1, 1))
        self.assertIs(summary["biggest_win"], self.tournament.get_match(1))
        self.assertIs(summary["highest_scoring"], self.tournament.get_match(1))
        self.assertEqual(analytics.clean_sheets(self.tournament)[self.real.id], 1)

        goals = analytics.goals_by_matchday(self.tournament)
        self.assertEqual([g["goals"] for g in goals], [4, 0, 3])

    def test_team_stats_and_discipline(self):
        stats = analytics.team_stats(self.tournament, self.liverpool)
        self.assertEqual(stats["rank"], 2)
        self.assertEqual(stats["form_string"], "DW")
        self.assertEqual(stats["clean_sheets"], 1)
        self.assertEqual(stats["yellow_cards"], 0)
        self.assertEqual(analytics.discipline_table(self.tournament), [])


# ---------------------------------------------------------------------- #
# Simulation & export
# ---------------------------------------------------------------------- #
class SimulationTests(unittest.TestCase):
    def test_simulate_season_respects_rules(self):
        tournament = make_league(5, players=3)
        tournament.generate_schedule()
        rng = random.Random(42)

        played = simulation.simulate_next_matchday(tournament, rng)
        self.assertEqual(len(played), 2)
        self.assertEqual(tournament.current_matchday, 2)

        rest = simulation.simulate_season(tournament, rng)
        self.assertEqual(len(rest), 8)
        self.assertTrue(tournament.is_complete)

        for match in tournament.matches:
            self.assertTrue(match.is_finished)
            for card in match.cards:
                self.assertTrue(match.is_participating(card["player"]))
                self.assertTrue(1 <= card["minute"] <= 90)

        with self.assertRaises(RuntimeError):
            simulation.simulate_season(tournament, rng)
        with self.assertRaises(RuntimeError):
            simulation.simulate_next_matchday(tournament, rng)

    def test_simulate_skips_inactive_and_non_upcoming(self):
        tournament = make_league(3, players=1)
        tournament.generate_schedule()
        tournament.set_team_active(3, False)
        rng = random.Random(1)

        played = simulation.simulate_season(tournament, rng)
        self.assertEqual([m.match_id for m in played], [1])

        with self.assertRaises(RuntimeError):
            simulation.simulate_match(tournament, tournament.get_match(1), rng)
        with self.assertRaises(ValueError):
            simulation.simulate_matchday(tournament, 99, rng)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tournament = build_sample_tournament()
        self.tournament.generate_schedule()
        self.tournament.start_match(1)
        self.tournament.record_card(1, 101, CardType.YELLOW, 40)
        self.tournament.finish_match(1, 2, 2)

    def test_rows_and_csv(self):
        rows = export.standings_rows(self.tournament)
        self.assertEqual(rows[0]["form"], "D")
        csv_text = export.rows_to_csv(rows)
        self.assertTrue(csv_text.startswith("rank,team,played"))
        self.assertEqual(len(csv_text.strip().splitlines()), 4)

        fixtures = export.fixtures_rows(self.tournament)
        self.assertEqual(fixtures[0]["winner"], "Draw")
        self.assertIsNone(fixtures[1]["home_goals"])
        self.assertEqual(export.cards_rows(self.tournament)[0]["minute"], 40)
        self.assertEqual(len(export.players_rows(self.tournament)), 4)
        self.assertEqual(export.rows_to_csv([]), "\r\n")

    def test_json_snapshot(self):
        data = json.loads(export.to_json(self.tournament))
        self.assertEqual(data["name"], "Elite Football League")
        self.assertEqual(len(data["teams"]), 3)
        self.assertEqual(data["matches"][0]["cards"][0]["player"], "Player One")
        self.assertEqual(data["summary"]["played"], 1)
        self.assertEqual(data["history"][0]["type"], EventType.TEAM_REGISTERED)

    def test_markdown_report(self):
        report = export.season_report_markdown(self.tournament)
        self.assertIn("# Elite Football League - Season report", report)
        self.assertIn("| 1 | ", report)
        self.assertIn("### Matchday 1", report)
        self.assertIn("Real Madrid 2 - 2 Barcelona", report)
        self.assertIn("## Discipline", report)


if __name__ == "__main__":
    unittest.main()
