# Images

Drop image files here and the app picks them up automatically
(png, jpg, jpeg, webp or svg; keep each under 1.5 MB).

| What | Path | Example |
|------|------|---------|
| Team crest | `assets/teams/<team id>.png` or `assets/teams/<team slug>.png` | `assets/teams/RM.png`, `assets/teams/real-madrid.png` |
| Player photo | `assets/players/<player id>.png` | `assets/players/101.png` |
| Dashboard backdrop | `assets/hero.jpg` | a wide stadium photo (about 1600 x 500) |

The slug is the team name in lower case with spaces and punctuation
replaced by `-` (shown in Teams & Players > Club identity).

Anything uploaded from the UI lives only in that browser session;
files in this folder are permanent.

Official club crests and player photographs are usually trademarked or
copyrighted: use images you own or that are licensed for your use.
Without an image the app draws a crest from the club's initials and
colour, an avatar from the player's initials, and a pitch behind the hero.
