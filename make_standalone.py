"""Wrap the artifact page source into a standalone, offline-viewable HTML file.

IN THE REPO deliberately (moved here 2026-08-17, along with the page source it reads). Both
previously lived in a Claude session scratchpad -- the same directory the Stage 3 executor was
lost from (REPORT.md 22). The page source is the ONLY copy of what was published, so losing it
would mean the live artifact could never be updated again, only replaced.

The published artifact is served inside a host skeleton (doctype, head, a minimal CSS reset)
that the source file does not carry. Opening the source directly in a browser would therefore
render without the reset and with the <title>/<style> stranded in the body. This adds the
skeleton back so the repo copy is a faithful, self-contained snapshot: no network, no CDN,
nothing external -- the whole page in one file.

Re-run after any artifact redeploy to refresh the repo snapshot.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

SOURCE = Path(__file__).with_name("artifact") / "kstar-calibration.html"
TARGET = Path(r"C:\MCXRAY\Sim\Wrapper\kstar_calibration_setA_report.html")
ARTIFACT_URL = "https://claude.ai/code/artifact/24626073-4341-4a38-9b72-88db52be13f2"

# Mirrors the reset the artifact host applies. Zeroing dl/dd matters here: the run-parameter
# and equation blocks sit in flex columns with `gap`, so a default 1em dl margin would
# double-space them relative to the published page.
RESET = """*, *::before, *::after { box-sizing: border-box; }
    body, h1, h2, h3, h4, p, figure, blockquote, dl, dd, ul, ol { margin: 0; padding: 0; }
    img, picture, svg { max-width: 100%; }
    button, input, select, textarea { font: inherit; }"""

# Emoji favicon as an inline SVG data URI -- keeps the file dependency-free.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='.9em' font-size='90'%3E%F0%9F%93%89%3C/text%3E%3C/svg%3E"
)


def build() -> Path:
    source = SOURCE.read_text(encoding="utf-8")

    match = re.search(r"<title>(.*?)</title>", source, re.S)
    if not match:
        raise SystemExit("no <title> found in the artifact source")
    title = match.group(1).strip()
    body = source.replace(match.group(0), "", 1).lstrip()

    stamp = dt.date.today().isoformat()
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="{FAVICON}">
<!--
  Standalone snapshot of the published artifact, taken {stamp}.
  Live version (master copy): {ARTIFACT_URL}

  Self-contained: no external scripts, styles, fonts or images. Opens offline from disk.
  Follows the operating system light/dark setting.

  This file = the artifact page source + the host skeleton the published version supplies
  at serve time, i.e. everything from <!doctype html> down to </style> below, plus the
  closing </body></html>. To republish this page as an artifact, strip that skeleton back
  off -- the Artifact tool wraps the content itself and rejects a full document.
-->
<style>
    {RESET}
</style>
</head>
<body>
{body}
</body>
</html>
"""
    TARGET.write_text(document, encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    out = build()
    print(f"{out}  ({out.stat().st_size:,} bytes)")
