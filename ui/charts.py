"""
Altair chart builders, all sharing one quiet theme.

Colour rules (see the dataviz method):
- one series  -> one hue (slot 1 blue)
- identity    -> the fixed categorical order below, never cycled
- polarity    -> blue (positive) / red (negative) around a zero baseline
- card charts -> the literal card colours, with a legend and labels
"""

import math

import altair as alt
import pandas as pd

from ui.styles import TOKENS

# Validated against the card surface (#13263a) in dark mode.
CATEGORICAL = [
    "#3987e5", "#d95926", "#199e70", "#c98500",
    "#d55181", "#008300", "#9085e9", "#e66767",
]
SERIES_1 = CATEGORICAL[0]
SERIES_2 = CATEGORICAL[1]
SERIES_3 = CATEGORICAL[2]
DEEMPHASIS = "#4e637a"
POSITIVE = "#3987e5"
NEGATIVE = "#e66767"
CARD_YELLOW = TOKENS["warn"]
CARD_RED = TOKENS["bad"]

SURFACE = TOKENS["surface"]
INK = TOKENS["ink"]
INK_2 = TOKENS["ink_2"]
INK_3 = TOKENS["ink_3"]
LINE = TOKENS["line"]
FONT = "Barlow, Segoe UI, system-ui, sans-serif"

BAR = 18          # px, never thicker than 24
ROW_HEIGHT = 30   # px per category on horizontal charts
MIN_SEGMENT_SHARE_FOR_LABEL = 0.12


def _theme(chart, height):
    """Transparent background, hairline grid, text in ink tokens."""
    return (
        chart.properties(
            height=height,
            background="transparent",
            padding={"left": 4, "right": 16, "top": 8, "bottom": 4},
        )
        .configure(font=FONT)
        .configure_axis(
            labelColor=INK_2,
            titleColor=INK_3,
            gridColor=LINE,
            gridWidth=1,
            domainColor=LINE,
            tickColor=LINE,
            labelFontSize=12,
            titleFontSize=12,
            titleFontWeight="normal",
            labelPadding=6,
            titlePadding=10,
        )
        .configure_view(strokeWidth=0)
        .configure_legend(
            orient="top",
            direction="horizontal",
            labelColor=INK_2,
            titleColor=INK_3,
            labelFontSize=12,
            symbolSize=90,
            symbolType="square",
            padding=0,
        )
    )


def _rows_height(count, minimum=140):
    return max(minimum, ROW_HEIGHT * count + 40)


def _int_ticks(low, high, max_ticks=8):
    """Whole-number tick values from `low` to `high`, at most ~max_ticks."""
    low, high = int(math.floor(low)), int(math.ceil(high))
    span = max(high - low, 1)
    step = max(1, math.ceil(span / max_ticks))
    start = math.floor(low / step) * step
    end = math.ceil(high / step) * step
    return list(range(start, end + 1, step))


def _headroom(value, share=0.15):
    """Room beyond the largest bar so its label never touches the edge."""
    return max(1, math.ceil(abs(value) * share))


def _int_axis(title, low, high, fmt="d"):
    return alt.Axis(values=_int_ticks(low, high), format=fmt, title=title)


# ---------------------------------------------------------------------- #
# Standings charts
# ---------------------------------------------------------------------- #
def points_bar(standings):
    """Ranked horizontal bars, one hue: points per team."""
    df = pd.DataFrame([
        {"team": r["team"].name, "points": r["points"], "rank": r["rank"],
         "played": r["played"], "goal_difference": r["goal_difference"]}
        for r in standings
    ])
    top = int(df["points"].max()) if len(df) else 0

    base = alt.Chart(df).encode(
        y=alt.Y("team:N", sort=alt.EncodingSortField("rank"), title=None,
                axis=alt.Axis(labelLimit=170, grid=False)),
        x=alt.X("points:Q", axis=_int_axis("Points", 0, top),
                scale=alt.Scale(domain=[0, top + _headroom(top)], nice=False)),
        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("points:Q", title="Points"),
            alt.Tooltip("played:Q", title="Played"),
            alt.Tooltip("goal_difference:Q", title="Goal difference"),
        ],
    )
    bars = base.mark_bar(size=BAR, cornerRadiusEnd=4, color=SERIES_1)
    labels = base.mark_text(align="left", dx=6, color=INK_2, fontSize=12).encode(
        text="points:Q"
    )
    return _theme(bars + labels, _rows_height(len(df)))


def goal_difference_bar(standings):
    """Diverging horizontal bars around zero: goal difference per team."""
    df = pd.DataFrame([
        {"team": r["team"].name, "goal_difference": r["goal_difference"],
         "rank": r["rank"], "goals_for": r["goals_for"], "goals_against": r["goals_against"]}
        for r in standings
    ])
    low = min(int(df["goal_difference"].min()), 0)
    high = max(int(df["goal_difference"].max()), 0)
    pad = _headroom(max(abs(low), abs(high)))
    positive = alt.datum.goal_difference >= 0

    base = alt.Chart(df).encode(
        y=alt.Y("team:N", sort=alt.EncodingSortField("rank"), title=None,
                axis=alt.Axis(labelLimit=170, grid=False)),
        x=alt.X("goal_difference:Q", axis=_int_axis("Goal difference", low, high, "+d"),
                scale=alt.Scale(domain=[low - pad, high + pad], nice=False)),
        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("goal_difference:Q", title="Goal difference", format="+d"),
            alt.Tooltip("goals_for:Q", title="Scored"),
            alt.Tooltip("goals_against:Q", title="Conceded"),
        ],
    )
    bars = base.mark_bar(size=BAR, cornerRadiusEnd=4).encode(
        color=alt.condition(positive, alt.value(POSITIVE), alt.value(NEGATIVE)),
    )
    pos_labels = base.transform_filter(positive).mark_text(
        align="left", dx=6, color=INK_2, fontSize=12
    ).encode(text=alt.Text("goal_difference:Q", format="+d"))
    neg_labels = base.transform_filter(~positive).mark_text(
        align="right", dx=-6, color=INK_2, fontSize=12
    ).encode(text=alt.Text("goal_difference:Q", format="+d"))
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=INK_3, strokeWidth=1).encode(x="x:Q")

    return _theme(zero + bars + pos_labels + neg_labels, _rows_height(len(df)))


def goals_for_against(standings):
    """Grouped horizontal bars: goals scored vs conceded per team (2 series)."""
    rows = []
    for r in standings:
        rows.append({"team": r["team"].name, "rank": r["rank"], "measure": "Scored", "goals": r["goals_for"]})
        rows.append({"team": r["team"].name, "rank": r["rank"], "measure": "Conceded", "goals": r["goals_against"]})
    df = pd.DataFrame(rows)
    top = int(df["goals"].max()) if len(df) else 0

    chart = alt.Chart(df).mark_bar(size=10, cornerRadiusEnd=3).encode(
        y=alt.Y("team:N", sort=alt.EncodingSortField("rank"), title=None,
                axis=alt.Axis(labelLimit=170, grid=False)),
        yOffset=alt.YOffset("measure:N", sort=["Scored", "Conceded"]),
        x=alt.X("goals:Q", axis=_int_axis("Goals", 0, top),
                scale=alt.Scale(domain=[0, top + _headroom(top, 0.08)], nice=False)),
        color=alt.Color("measure:N", title=None,
                        scale=alt.Scale(domain=["Scored", "Conceded"], range=[SERIES_1, SERIES_2])),
        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("measure:N", title="Measure"),
            alt.Tooltip("goals:Q", title="Goals"),
        ],
    )
    return _theme(chart, _rows_height(len(standings), minimum=160) + 20)


# ---------------------------------------------------------------------- #
# History charts
# ---------------------------------------------------------------------- #
def position_race(rows, highlight):
    """
    Position after every matchday. One team is emphasised in blue,
    the rest recede to grey so the story stays readable.
    """
    # Only the plotted columns: team IDs can mix ints and strings.
    df = pd.DataFrame(rows)[["matchday", "team", "rank", "points"]]
    team_count = df["team"].nunique()
    last_matchday = int(df["matchday"].max())
    is_highlight = alt.datum.team == highlight

    base = alt.Chart(df).encode(
        x=alt.X("matchday:O", title="Matchday", axis=alt.Axis(labelAngle=0, grid=False)),
        y=alt.Y("rank:Q", title="Position",
                scale=alt.Scale(domain=[team_count + 0.5, 0.5]),
                axis=alt.Axis(values=list(range(1, team_count + 1)), format="d")),
        detail="team:N",
    )
    others = base.transform_filter(~is_highlight).mark_line(
        strokeWidth=2, color=DEEMPHASIS, opacity=0.75, strokeCap="round", strokeJoin="round"
    )
    line = base.transform_filter(is_highlight).mark_line(
        strokeWidth=3, color=SERIES_1, strokeCap="round", strokeJoin="round"
    )
    dots = base.transform_filter(is_highlight).mark_point(
        filled=True, size=80, color=SERIES_1, stroke=SURFACE, strokeWidth=2
    )
    label = base.transform_filter(
        is_highlight & (alt.datum.matchday == last_matchday)
    ).mark_text(align="left", dx=12, color=INK, fontSize=12, fontWeight="bold").encode(
        text="team:N"
    )
    hover = base.mark_point(opacity=0, size=260).encode(
        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("matchday:O", title="After matchday"),
            alt.Tooltip("rank:Q", title="Position"),
            alt.Tooltip("points:Q", title="Points"),
        ],
    )
    chart = others + line + dots + label + hover
    return _theme(chart, max(220, 26 * team_count + 80)).properties(
        padding={"left": 4, "right": 90, "top": 8, "bottom": 4}
    )


def goals_per_matchday(rows):
    """Single-series area + line: goals scored on each played matchday."""
    df = pd.DataFrame(rows)
    top = int(df["goals"].max()) if len(df) else 0

    base = alt.Chart(df).encode(
        x=alt.X("matchday:O", title="Matchday", axis=alt.Axis(labelAngle=0, grid=False)),
        y=alt.Y("goals:Q", axis=_int_axis("Goals", 0, top),
                scale=alt.Scale(domain=[0, top + _headroom(top, 0.1)], nice=False)),
        tooltip=[
            alt.Tooltip("matchday:O", title="Matchday"),
            alt.Tooltip("goals:Q", title="Goals"),
            alt.Tooltip("matches:Q", title="Matches played"),
            alt.Tooltip("cards:Q", title="Cards"),
        ],
    )
    area = base.mark_area(color=SERIES_1, opacity=0.12, interpolate="monotone")
    line = base.mark_line(color=SERIES_1, strokeWidth=2, interpolate="monotone", strokeCap="round")
    dots = base.mark_point(filled=True, size=80, color=SERIES_1, stroke=SURFACE, strokeWidth=2)
    return _theme(area + line + dots, 220)


def results_breakdown(breakdown):
    """Tall segmented bar: how finished matches ended."""
    parts = [
        ("Home wins", breakdown["home_wins"], SERIES_1),
        ("Draws", breakdown["draws"], SERIES_2),
        ("Away wins", breakdown["away_wins"], SERIES_3),
    ]
    total = sum(count for _, count, _ in parts) or 1
    df = pd.DataFrame([
        {
            "outcome": name,
            "count": count,
            "order": i,
            # Only label a block wide enough to hold its text.
            "share": f"{count / total:.0%}" if count / total >= MIN_SEGMENT_SHARE_FOR_LABEL else "",
        }
        for i, (name, count, _) in enumerate(parts)
        if count > 0
    ])
    domain = [name for name, _, _ in parts]
    colors = [color for _, _, color in parts]

    base = alt.Chart(df).encode(
        x=alt.X("count:Q", stack="zero", title=None, axis=None),
        order=alt.Order("order:Q"),
        color=alt.Color("outcome:N", title=None, scale=alt.Scale(domain=domain, range=colors)),
        tooltip=[alt.Tooltip("outcome:N", title="Outcome"), alt.Tooltip("count:Q", title="Matches")],
    )
    bar = base.mark_bar(size=28, cornerRadius=4, stroke=SURFACE, strokeWidth=2)
    # Text sits at each block's trailing edge, pulled inside by dx.
    # The colour must be a constant here, or the text inherits the block colour.
    text = base.mark_text(align="right", dx=-8, fontSize=12, fontWeight="bold").encode(
        text="share:N",
        color=alt.value("#ffffff"),
    )
    return _theme(bar + text, 70)


def cards_by_team(rows):
    """Stacked horizontal bars with the literal card colours."""
    long_rows = []
    for r in rows:
        total = r["yellow"] + r["red"]
        long_rows.append({"team": r["team"], "card": "Yellow cards", "count": r["yellow"], "total": total})
        long_rows.append({"team": r["team"], "card": "Red cards", "count": r["red"], "total": total})
    df = pd.DataFrame(long_rows)
    top = int(df["total"].max()) if len(df) else 0

    chart = alt.Chart(df).mark_bar(size=BAR, cornerRadiusEnd=4, stroke=SURFACE, strokeWidth=2).encode(
        y=alt.Y("team:N", sort=alt.EncodingSortField("total", order="descending"), title=None,
                axis=alt.Axis(labelLimit=170, grid=False)),
        x=alt.X("count:Q", axis=_int_axis("Cards", 0, top),
                scale=alt.Scale(domain=[0, top + _headroom(top, 0.08)], nice=False)),
        order=alt.Order("card:N", sort="descending"),
        color=alt.Color("card:N", title=None,
                        scale=alt.Scale(domain=["Yellow cards", "Red cards"], range=[CARD_YELLOW, CARD_RED])),
        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("card:N", title="Card"),
            alt.Tooltip("count:Q", title="Count"),
        ],
    )
    # Extra room: the legend and axis title share the height with the rows.
    return _theme(chart, max(180, 34 * len(rows) + 80))
