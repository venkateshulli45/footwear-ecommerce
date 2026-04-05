import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.db import connection  # noqa: E402


def main() -> None:
    table = "categoryc_mfm"
    with connection.cursor() as cur:
        cur.execute(
            """
            select column_name
            from information_schema.columns
            where table_name = %s
            order by ordinal_position
            """,
            [table],
        )
        cols = [r[0] for r in cur.fetchall()]
    print(table, "columns:", cols)


if __name__ == "__main__":
    main()

