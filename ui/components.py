"""
HTML components rendered with st.html. Every piece of user text goes
through `esc`, so team and player names can never inject markup.
"""

from html import escape as esc

import streamlit as st

from league import FORM_GUIDE_LENGTH, MatchStatus, SeasonPhase, analytics
from ui.assets import SVG_DEFS, hero_backdrop, player_avatar, team_crest
from ui.helpers import fmt_clock, fmt_stamp, plural
from ui.icons import icon


def render(markup):
    """
    Render component markup. st.html sanitises away inline <svg>, which
    the crests and icons need, so components go through st.markdown as a
    single-line HTML block (no Markdown parsing happens inside it).
    """
    st.markdown(f'<div class="ea-root">{markup}</div>', unsafe_allow_html=True)


def svg_defs():
    """Shared gradient definitions used by the generated crests."""
    render(SVG_DEFS)


# ---------------------------------------------------------------------- #
# Headings
# ---------------------------------------------------------------------- #
# Headings are divs with a heading role: st.markdown rewrites real <h1>-<h3>
# tags into its own anchored heading component, which breaks the layout.
def page_header(title, subtitle="", aside="", icon_name=None):
    mark = icon(icon_name, size=26) if icon_name else ""
    render(
        f'<div class="ea-head"><div><div class="t" role="heading" aria-level="1">{mark}{esc(title)}</div>'
        f'<p>{esc(subtitle)}</p></div><div>{aside}</div></div>'
    )


def section(title, caption=""):
    render(
        f'<div class="ea-sec"><div class="h" role="heading" aria-level="2">{esc(title)}</div>'
        f'<span>{esc(caption)}</span></div>'
    )


def tab_bar(key, options):
    """
    A tab strip that survives reruns. st.tabs forgets its selection after
    st.rerun(), so this is a horizontal radio styled as tabs (see styles.py).
    Returns the selected option; render only that section.
    """
    with st.container(key=f"tabs-{key}"):
        return st.radio(
            "Section", options, horizontal=True, key=key, label_visibility="collapsed"
        )


def empty_state(title, text, steps=(), icon_name="sparkles"):
    items = "".join(f"<li>{esc(step)}</li>" for step in steps)
    ordered = f"<ol>{items}</ol>" if items else ""
    render(
        f'<div class="ea-empty"><div class="ic">{icon(icon_name, size=28)}</div>'
        f'<div><div class="h" role="heading" aria-level="3">{esc(title)}</div>'
        f"<p>{esc(text)}</p>{ordered}</div></div>"
    )


# ---------------------------------------------------------------------- #
# Pills
# ---------------------------------------------------------------------- #
def pill(text, tone=""):
    return f'<span class="ea-pill {tone}">{esc(text)}</span>'


def phase_pill(phase):
    tone = {
        SeasonPhase.SETUP: "",
        SeasonPhase.READY: "gold",
        SeasonPhase.IN_PROGRESS: "",
        SeasonPhase.COMPLETE: "gold",
    }.get(phase, "")
    return pill(phase, tone)


def status_pill(match):
    if match.is_live:
        return pill("Live", "live")
    if match.is_finished:
        return pill("Full time")
    return pill("Upcoming")


# ---------------------------------------------------------------------- #
# Hero
# ---------------------------------------------------------------------- #
def hero(tournament, summary, leader=None):
    played, total = summary["played"], summary["fixtures"]
    pct = (played / total * 100) if total else 0
    backdrop, has_photo = hero_backdrop()

    meta = [
        f"<span>{icon('users')}<b>{summary['teams']}</b> {'team' if summary['teams'] == 1 else 'teams'}</span>",
        f"<span>{icon('user-round')}<b>{summary['players']}</b> {'player' if summary['players'] == 1 else 'players'}</span>",
    ]
    if total:
        meta.append(f"<span>{icon('calendar-days')}<b>{total}</b> fixtures</span>")
        if summary["current_matchday"]:
            meta.append(
                f"<span>{icon('timer')}Matchday <b>{summary['current_matchday']}</b> of "
                f"<b>{summary['matchdays']}</b></span>"
            )
    if summary["goals"]:
        meta.append(
            f"<span>{icon('goal')}<b>{summary['goals']}</b> goals, "
            f"<b>{summary['goals_per_match']}</b> per match</span>"
        )

    meter = ""
    if total:
        meter = (
            f'<div class="ea-meter"><div class="track">'
            f'<div class="fill" style="width:{pct:.1f}%"></div></div>'
            f'<div class="cap"><span>{played} of {total} fixtures played</span>'
            f"<span>{pct:.0f}%</span></div></div>"
        )

    if leader is not None and leader["played"]:
        form = form_pills(analytics.team_form(tournament, leader["team"]))
        crown = "Champion" if tournament.is_complete else "Leader"
        mark = icon("trophy" if tournament.is_complete else "crown", size=16)
        right = (
            f'<div class="leader"><div class="lbl">{mark}{crown}</div>'
            f'<div class="team">{team_crest(leader["team"], 48)}'
            f'<span>{esc(leader["team"].name)}</span></div>'
            f'<div class="pts"><span><b>{leader["points"]}</b> pts</span>'
            f'<span>{leader["won"]}W {leader["drawn"]}D {leader["lost"]}L</span>'
            f"{form}</div></div>"
        )
    else:
        hint = {
            SeasonPhase.SETUP: "Register at least two teams to get started.",
            SeasonPhase.READY: "Generate the schedule to start the season.",
        }.get(tournament.phase, "Play the first match to see a leader here.")
        right = (
            f'<div class="leader"><div class="lbl">{icon("crown", size=16)}Leader</div>'
            f'<div class="team muted"><span>No results yet</span></div>'
            f'<div class="pts">{esc(hint)}</div></div>'
        )

    render(
        f'<div class="ea-hero{" has-photo" if has_photo else ""}" style="{backdrop}"><div>'
        f'<div class="name">{esc(tournament.name)}{phase_pill(tournament.phase)}</div>'
        f'<div class="meta">{"".join(meta)}</div>{meter}</div>{right}</div>'
    )


# ---------------------------------------------------------------------- #
# Scoreboards & results
# ---------------------------------------------------------------------- #
def _goal(match, index):
    if match.score is None:
        return "–"
    return str(match.score[index])


def _lost_class(match, team):
    if match.is_finished and match.winner is not None and match.winner is not team:
        return " lost"
    return ""


def team_badge(team, size=22, cls="ea-team"):
    return f'<span class="{cls}">{team_crest(team, size)}<span>{esc(team.name)}</span></span>'


def scoreboard(match, index=0):
    live = " live" if match.is_live else ""
    foot_left = f"Matchday {match.matchday}" if match.matchday else f"Match {match.match_id}"
    return (
        f'<div class="ea-score{live}" style="--i:{index}">'
        f'<div class="t{_lost_class(match, match.team1)}">{team_badge(match.team1, 22)}</div>'
        f'<div class="g{_lost_class(match, match.team1)}">{_goal(match, 0)}</div>'
        f'<div class="t{_lost_class(match, match.team2)}">{team_badge(match.team2, 22)}</div>'
        f'<div class="g{_lost_class(match, match.team2)}">{_goal(match, 1)}</div>'
        f'<div class="foot"><span>{esc(foot_left)}</span>{status_pill(match)}</div>'
        f"</div>"
    )


def scoreboard_strip(matches):
    render(
        '<div class="ea-strip">'
        + "".join(scoreboard(m, i) for i, m in enumerate(matches))
        + "</div>"
    )


def fixture_header(match):
    live = " live" if match.is_live else ""
    score = f"{_goal(match, 0)} – {_goal(match, 1)}" if match.score else "vs"
    when = ""
    if match.finished_at:
        when = f"Full time {fmt_stamp(match.finished_at)}"
    elif match.started_at:
        when = f"Kicked off {fmt_stamp(match.started_at)}"

    return (
        f'<div class="ea-fx">'
        f'<div class="h"><div><div class="t{_lost_class(match, match.team1)}">{esc(match.team1.name)}</div>'
        f'<div class="sub">{plural(len(match.team1.available_players), "available player")}</div></div>'
        f"{team_crest(match.team1, 56)}</div>"
        f'<div class="s{live}">{score}</div>'
        f'<div class="a">{team_crest(match.team2, 56)}'
        f'<div><div class="t{_lost_class(match, match.team2)}">{esc(match.team2.name)}</div>'
        f'<div class="sub">{plural(len(match.team2.available_players), "available player")}</div></div></div>'
        f'<div class="meta"><span>Match {esc(str(match.match_id))}</span>'
        f"<span>Matchday {match.matchday}</span>{status_pill(match)}"
        f"<span>{esc(when)}</span></div></div>"
    )


def result_row(match, index=0):
    live = " live" if match.is_live else ""
    score = f"{_goal(match, 0)} – {_goal(match, 1)}" if match.score or match.is_live else "vs"
    sub = f"Matchday {match.matchday}"
    if match.finished_at:
        sub = f"{sub}, full time {fmt_stamp(match.finished_at)}"
    return (
        f'<div class="ea-res" style="--i:{index}">'
        f'<div class="h{_lost_class(match, match.team1)}">{team_badge(match.team1, 20, "ea-team rev")}</div>'
        f'<div class="s{live}">{score}</div>'
        f'<div class="a{_lost_class(match, match.team2)}">{team_badge(match.team2, 20)}</div>'
        f'<div class="sub">{esc(sub)}</div></div>'
    )


def results_list(matches):
    render("".join(result_row(m, i) for i, m in enumerate(matches)))


# ---------------------------------------------------------------------- #
# Stat tiles
# ---------------------------------------------------------------------- #
def stat_tile(label, value, note="", tone="", unit="", icon_name=None, index=0):
    unit_html = f"<small>{esc(unit)}</small>" if unit else ""
    mark = f'<span class="ic">{icon(icon_name, size=20)}</span>' if icon_name else ""
    return (
        f'<div class="ea-tile {tone}" style="--i:{index}">{mark}<div class="l">{esc(label)}</div>'
        f'<div class="v">{esc(str(value))}{unit_html}</div>'
        f'<div class="n">{esc(note)}</div></div>'
    )


def stat_row(tiles):
    """tiles: list of dicts accepted by stat_tile(**tile)."""
    for index, (col, tile) in enumerate(zip(st.columns(len(tiles), gap="small"), tiles)):
        with col:
            render(stat_tile(index=index, **tile))


# ---------------------------------------------------------------------- #
# Form & standings
# ---------------------------------------------------------------------- #
def form_pills(entries, length=FORM_GUIDE_LENGTH):
    cells = [
        f'<span class="{e["result"]}" title="{esc(_form_title(e))}">{e["result"]}</span>'
        for e in entries[-length:]
    ]
    while len(cells) < length:
        cells.insert(0, '<span class="none"></span>')
    cells = [c.replace("<span ", f'<span style="--i:{i}" ', 1) for i, c in enumerate(cells)]
    return '<span class="ea-form">' + "".join(cells) + "</span>"


def _form_title(entry):
    venue = "vs" if entry["home"] else "at"
    return (
        f"{venue} {entry['opponent'].name} "
        f"{entry['goals_for']}-{entry['goals_against']} (matchday {entry['matchday']})"
    )


def standings_table(tournament, rows=None, compact=False, highlight=None):
    rows = tournament.get_standings() if rows is None else rows

    if compact:
        head = "<th></th><th class='left'>Team</th><th class='left'>Form</th><th>P</th><th>GD</th><th>Pts</th>"
    else:
        head = (
            "<th></th><th class='left'>Team</th><th class='left'>Form</th><th>P</th><th>W</th>"
            "<th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th>"
        )

    body = []
    for row in rows:
        team = row["team"]
        classes = []
        if row["rank"] == 1 and row["played"]:
            classes.append("first")
        if not team.is_active:
            classes.append("inactive")
        if highlight is not None and team is highlight:
            classes.append("hl")

        form = form_pills(analytics.team_form(tournament, team))
        badge = "" if team.is_active else "<small>inactive</small>"
        cells = [
            f'<td class="rank">{row["rank"]}</td>',
            f'<td class="team">{team_badge(team, 24)}{badge}</td>',
            f"<td>{form}</td>",
            f'<td class="num">{row["played"]}</td>',
        ]
        if not compact:
            cells += [
                f'<td class="num">{row["won"]}</td>',
                f'<td class="num">{row["drawn"]}</td>',
                f'<td class="num">{row["lost"]}</td>',
                f'<td class="num">{row["goals_for"]}</td>',
                f'<td class="num">{row["goals_against"]}</td>',
            ]
        cells += [
            f'<td class="num">{row["goal_difference"]:+d}</td>',
            f'<td class="pts">{row["points"]}</td>',
        ]
        body.append(f'<tr class="{" ".join(classes)}">{"".join(cells)}</tr>')

    render(
        '<div class="ea-table-wrap"><table class="ea-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


# ---------------------------------------------------------------------- #
# People & clubs
# ---------------------------------------------------------------------- #
def player_cards(players):
    cards = []
    for index, player in enumerate(players):
        banned = " banned" if player.is_banned else ""
        status = "Banned" if player.is_banned else "Available"
        cards.append(
            f'<div class="ea-player{banned}" style="--i:{index}">{player_avatar(player, 44)}'
            f'<div><div class="n">{esc(player.name)}</div>'
            f'<div class="r">{esc(player.role)}, #{esc(str(player.id))}</div></div>'
            f'<span class="st">{status}</span></div>'
        )
    render('<div class="ea-players">' + "".join(cards) + "</div>")


def club_cards(teams):
    cards = []
    for index, team in enumerate(teams):
        inactive = "" if team.is_active else " inactive"
        cards.append(
            f'<div class="ea-club{inactive}" style="--i:{index}">{team_crest(team, 44)}'
            f'<div><div class="n">{esc(team.name)}</div>'
            f'<div class="r">ID {esc(str(team.id))}, {plural(len(team.players), "player")}'
            f'{"" if team.is_active else ", inactive"}</div></div></div>'
        )
    render('<div class="ea-clubs">' + "".join(cards) + "</div>")


def club_identity(team, stats):
    """Big crest + name + the headline numbers, for the Teams page."""
    render(
        f'<div class="ea-club-hero">{team_crest(team, 84)}'
        f'<div><div class="n">{esc(team.name)}</div>'
        f'<div class="r">{plural(stats["players"], "player")}, '
        f'{plural(stats["banned"], "banned player")}, '
        f'{"active" if team.is_active else "inactive"}</div>'
        f'<div class="f"><span>Last five</span>{form_pills(stats["form"])}</div></div></div>'
    )


# ---------------------------------------------------------------------- #
# Timeline & head-to-head
# ---------------------------------------------------------------------- #
EVENT_ICONS = {
    "team_registered": "shield",
    "team_removed": "x",
    "team_activated": "circle-check",
    "team_deactivated": "ban",
    "player_added": "user-plus",
    "player_removed": "user-x",
    "player_banned": "ban",
    "player_unbanned": "circle-check",
    "schedule_generated": "calendar-days",
    "match_started": "play",
    "card": "rectangle-vertical",
    "send_off": "flag",
    "match_finished": "timer",
}


def timeline(events, limit=None, clock_only=False):
    shown = events[:limit] if limit else events
    items = []
    for index, event in enumerate(shown):
        when = fmt_clock(event.timestamp) if clock_only else fmt_stamp(event.timestamp)
        mark = icon(EVENT_ICONS.get(event.type, "clock"), size=12)
        items.append(
            f'<li class="{esc(event.type)}" style="--i:{index}"><span class="dot">{mark}</span>'
            f'<span class="when">{esc(when)}</span>'
            f'<span class="what"><b>{esc(event.label)}</b>{esc(event.message)}</span></li>'
        )
    render('<ul class="ea-tl">' + "".join(items) + "</ul>")


def head_to_head_card(record):
    a, b = record["team_a"], record["team_b"]
    render(
        f'<div class="ea-vs">'
        f'<div class="side"><div class="t">{team_crest(a, 56)}<span>{esc(a.name)}</span></div>'
        f'<div class="sub">{plural(record["wins_a"], "win")}, {plural(record["goals_a"], "goal")}</div></div>'
        f'<div class="rec">{record["wins_a"]} – {record["draws"]} – {record["wins_b"]}'
        f'<small>wins, draws, wins ({record["played"]} played)</small></div>'
        f'<div class="side r"><div class="t r"><span>{esc(b.name)}</span>{team_crest(b, 56)}</div>'
        f'<div class="sub r">{plural(record["wins_b"], "win")}, {plural(record["goals_b"], "goal")}</div></div>'
        f"</div>"
    )


def status_counts_text(tournament):
    live = len(tournament.get_matches_by_status(MatchStatus.LIVE))
    return f"{live} live" if live else ""
