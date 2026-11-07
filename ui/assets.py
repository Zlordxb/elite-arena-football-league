"""
Images: team crests, player photos and the hero backdrop.

Every image is resolved in this order:
1. a file uploaded in this browser session (Teams & Players / Manage League),
2. a file in the assets/ folder:
       assets/teams/<team id or team slug>.png   (also jpg, jpeg, webp, svg)
       assets/players/<player id>.png
       assets/hero.jpg
3. a generated placeholder: an SVG crest with the club's initials, an
   avatar with the player's initials, or a drawn pitch behind the hero.

The domain package never sees images; they are a presentation concern.
"""

import base64
import mimetypes
import re
import zlib
from html import escape as esc
from pathlib import Path
from urllib.parse import quote

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FOLDERS = {
    "teams": ASSETS_DIR / "teams",
    "players": ASSETS_DIR / "players",
    "hero": ASSETS_DIR,
}
IMAGE_TYPES = ("png", "jpg", "jpeg", "webp", "svg")
MAX_IMAGE_BYTES = 1_500_000

# Crest colours: saturated enough to carry white initials, distinct from
# the chart palette so a crest never looks like a data series.
CREST_COLORS = (
    "#1d4ed8", "#b91c1c", "#047857", "#6d28d9", "#b45309",
    "#0e7490", "#be185d", "#4d7c0f", "#9f1239", "#1e3a8a",
)
AVATAR_FALLBACK = "#3b4c63"


# ---------------------------------------------------------------------- #
# Session state
# ---------------------------------------------------------------------- #
def init_assets_state():
    st.session_state.setdefault("uploads", {"teams": {}, "players": {}, "hero": {}})
    st.session_state.setdefault("team_colors", {})
    st.session_state.setdefault("uploader_nonce", 0)


def _uploads(kind):
    return st.session_state.uploads[kind]


def save_upload(kind, key, uploaded):
    """Validate an UploadedFile and keep it for this session."""
    if uploaded is None:
        raise ValueError("Choose an image file first.")

    extension = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
    if extension not in IMAGE_TYPES:
        raise ValueError(f"Use one of: {', '.join(IMAGE_TYPES)}.")

    if uploaded.size > MAX_IMAGE_BYTES:
        raise ValueError(f"Image must be smaller than {MAX_IMAGE_BYTES // 1_000_000} MB.")

    mime = "image/svg+xml" if extension == "svg" else (uploaded.type or f"image/{extension}")
    _uploads(kind)[_key(key)] = (uploaded.getvalue(), mime)
    st.session_state.uploader_nonce += 1
    return uploaded.name


def remove_upload(kind, key=None):
    _uploads(kind).pop(_key(key), None)
    st.session_state.uploader_nonce += 1


def has_upload(kind, key=None):
    return _key(key) in _uploads(kind)


def uploader_key(name):
    """A key that changes after every save/remove, so the widget resets."""
    return f"{name}_{st.session_state.uploader_nonce}"


def _key(key):
    return "hero" if key is None else str(key)


# ---------------------------------------------------------------------- #
# Image lookup
# ---------------------------------------------------------------------- #
def slug(text):
    text = re.sub(r"[^a-z0-9]+", "-", str(text).casefold()).strip("-")
    return text or "team"


@st.cache_data(show_spinner=False)
def _read_bytes(path_str, _mtime):
    return Path(path_str).read_bytes()


def _asset_file(kind, keys):
    folder = FOLDERS[kind]

    for key in keys:
        for extension in IMAGE_TYPES:
            candidate = folder / f"{key}.{extension}"
            if candidate.is_file():
                return candidate

    return None


def _data_url(data, mime):
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def image_url(kind, key=None, extra_keys=()):
    """Data URL for a session upload or an assets/ file, else None."""
    upload = _uploads(kind).get(_key(key))
    if upload is not None:
        return _data_url(*upload)

    keys = ["hero"] if kind == "hero" else [str(key), *extra_keys]
    path = _asset_file(kind, keys)
    if path is None:
        return None

    mime = "image/svg+xml" if path.suffix == ".svg" else (
        mimetypes.guess_type(path.name)[0] or "image/png"
    )
    return _data_url(_read_bytes(str(path), path.stat().st_mtime), mime)


def has_custom_image(kind, key=None, extra_keys=()):
    return image_url(kind, key, extra_keys) is not None


# ---------------------------------------------------------------------- #
# Crests & avatars
# ---------------------------------------------------------------------- #
def team_color(team):
    chosen = st.session_state.team_colors.get(team.id)
    if chosen:
        return chosen

    digest = zlib.crc32(team.name.casefold().encode("utf-8"))
    return CREST_COLORS[digest % len(CREST_COLORS)]


def set_team_color(team, color):
    st.session_state.team_colors[team.id] = color


def initials(name, limit=3):
    words = [w for w in re.split(r"[\s\-]+", str(name)) if w]
    letters = "".join(w[0] for w in words[:limit]).upper()
    return letters or "?"


def crest_svg(team):
    color = team_color(team)
    text = initials(team.name)
    size = {1: 30, 2: 26, 3: 21}.get(len(text), 18)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true">'
        f'<path d="M32 4 L56 11 V30 C56 45 45 55 32 60 C19 55 8 45 8 30 V11 Z" fill="{color}"/>'
        '<path d="M32 4 L56 11 V30 C56 45 45 55 32 60 C19 55 8 45 8 30 V11 Z" '
        'fill="url(#ea-shine)" opacity=".35"/>'
        '<path d="M32 9 L51 14.5 V30 C51 42 42 50.5 32 55 C22 50.5 13 42 13 30 V14.5 Z" '
        'fill="none" stroke="rgba(255,255,255,.35)" stroke-width="1.5"/>'
        f'<text x="32" y="{36 + (size - 21) * 0.18:.1f}" text-anchor="middle" '
        f'font-family="Barlow Condensed, Barlow, sans-serif" font-weight="700" '
        f'font-size="{size}" fill="#fff">{esc(text)}</text></svg>'
    )


def team_crest(team, size=28):
    """Crest image if the club has one, else the generated shield."""
    url = image_url("teams", team.id, extra_keys=(slug(team.name),))
    body = (
        f'<img src="{url}" alt="">' if url else crest_svg(team)
    )
    return (
        f'<span class="ea-crest" style="width:{size}px;height:{size}px" '
        f'title="{esc(team.name)}">{body}</span>'
    )


def player_avatar(player, size=40):
    url = image_url("players", player.id)
    color = team_color(player.team) if player.team is not None else AVATAR_FALLBACK
    font = max(11, round(size * 0.38))

    if url:
        body = f'<img src="{url}" alt="">'
    else:
        body = f'<span style="font-size:{font}px">{esc(initials(player.name, 2))}</span>'

    return (
        f'<span class="ea-avatar" style="width:{size}px;height:{size}px;'
        f'background:{color}">{body}</span>'
    )


# ---------------------------------------------------------------------- #
# Hero backdrop
# ---------------------------------------------------------------------- #
# The shared gradient defs live in a hidden SVG injected once per page
# (see components.svg_defs), so every crest can reference #ea-shine.
SVG_DEFS = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
    '<linearGradient id="ea-shine" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/>'
    "</linearGradient></defs></svg>"
)


def _pitch_svg():
    """A drawn football pitch, used behind the hero when no photo is set."""
    line = "rgba(255,255,255,0.07)"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" '
        'preserveAspectRatio="xMidYMid slice">'
        '<defs><radialGradient id="l1" cx="15%" cy="0%" r="60%">'
        '<stop offset="0" stop-color="#e9b949" stop-opacity=".16"/>'
        '<stop offset="1" stop-color="#e9b949" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="l2" cx="90%" cy="100%" r="55%">'
        '<stop offset="0" stop-color="#0ca30c" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#0ca30c" stop-opacity="0"/></radialGradient></defs>'
        '<rect width="1200" height="420" fill="#13263a"/>'
        '<rect width="1200" height="420" fill="url(#l1)"/>'
        '<rect width="1200" height="420" fill="url(#l2)"/>'
        f'<g fill="none" stroke="{line}" stroke-width="2">'
        '<rect x="60" y="40" width="1080" height="340"/>'
        '<line x1="600" y1="40" x2="600" y2="380"/>'
        '<circle cx="600" cy="210" r="70"/>'
        '<rect x="60" y="110" width="150" height="200"/>'
        '<rect x="990" y="110" width="150" height="200"/>'
        '<rect x="60" y="160" width="55" height="100"/>'
        '<rect x="1085" y="160" width="55" height="100"/>'
        '<path d="M210 170 A70 70 0 0 1 210 250"/>'
        '<path d="M990 170 A70 70 0 0 0 990 250"/>'
        "</g></svg>"
    )


def hero_backdrop():
    """(style attribute value, has_photo) for the hero container."""
    url = image_url("hero")

    if url:
        overlay = (
            "linear-gradient(90deg, rgba(11,22,38,.96) 0%, rgba(11,22,38,.82) 50%, "
            "rgba(11,22,38,.58) 100%)"
        )
        return f"background-image:{overlay},url({url})", True

    pitch = "data:image/svg+xml;charset=utf-8," + quote(_pitch_svg())
    return f"background-image:url({pitch})", False
