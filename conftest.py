"""Repo-root conftest, so `mcxray_wrapper` and `tests` import under pytest.

pytest already prepends this directory to sys.path by virtue of this file existing; the
explicit insert makes that contract visible rather than incidental.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
