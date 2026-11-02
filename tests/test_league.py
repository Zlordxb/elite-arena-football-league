"""
Unit tests for the league domain.

Run with:
    python -m unittest -v
"""

import unittest

from league import (
    CardType,
    FootballMatch,
    HumanPlayer,
    MatchStatus,
    SendOffReason,
    Team,
    Tournament,
    build_sample_tournament,
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

        with self.assertRaises(RuntimeError):
            match.finish_match(1, 0)

        match.start_match()
        self.assertTrue(match.is_live)

        with self.assertRaises(RuntimeError):
            match.start_match()

        match.finish_match(2, 1)
        self.assertTrue(match.is_finished)
        self.assertEqual(match.score, (2, 1))
        self.assertEqual(match.get_result()["winner"], "A")

        with self.assertRaises(RuntimeError):
            match.finish_match(0, 0)

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

    def test_banned_player_cannot_receive_card(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]
        player.ban()
        with self.assertRaises(ValueError):
            match.add_card(player, CardType.YELLOW)

    def test_two_yellows_send_off(self):
        match, t1, _ = make_live_match()
        player = t1.players[0]

        match.add_card(player, "Yellow")
        self.assertEqual(match.yellow_cards_for(player), 1)
        self.assertFalse(match.is_sent_off(player))

        match.add_card(player, "yellow")
        self.assertTrue(match.is_sent_off(player))
        self.assertEqual(match.red_cards[0]["reason"], SendOffReason.SECOND_YELLOW)

        with self.assertRaises(ValueError):
            match.add_card(player, CardType.YELLOW)

        details = match.get_match_details()
        self.assertEqual(details["yellow_cards"], 2)
        self.assertEqual(details["red_cards"], 1)
        self.assertEqual(details["sent_off_players"], [player.id])

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
        with self.assertRaises(ValueError):
            tournament.generate_schedule()

        beta = make_team(2, "Beta")
        beta.deactivate()
        tournament.register_team(beta)
        with self.assertRaises(ValueError):
            tournament.generate_schedule()

    def test_round_robin_schedule(self):
        tournament = build_sample_tournament()
        matches = tournament.generate_schedule()

        self.assertEqual(len(matches), 3)
        self.assertEqual([m.match_id for m in matches], [1, 2, 3])
        self.assertTrue(tournament.schedule_generated)

        with self.assertRaises(RuntimeError):
            tournament.generate_schedule()
        with self.assertRaises(RuntimeError):
            tournament.register_team(make_team(9, "Late"))
        with self.assertRaises(RuntimeError):
            tournament.unregister_team(1)

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

    def test_standings(self):
        tournament = build_sample_tournament()
        tournament.generate_schedule()

        # 1: Real Madrid 3-1 Barcelona, 2: Real Madrid 0-0 Liverpool,
        # 3: Barcelona 1-2 Liverpool
        for match_id, score in ((1, (3, 1)), (2, (0, 0)), (3, (1, 2))):
            match = tournament.get_match(match_id)
            match.start_match()
            match.finish_match(*score)

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


if __name__ == "__main__":
    unittest.main()
