import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import get_session_factory, init_db
from app.services.behavior import seed_sample_behavior


def main() -> None:
    init_db()
    session = get_session_factory()()
    try:
        total = seed_sample_behavior(session)
    finally:
        session.close()

    print(f"Seeded behavior events available: {total}")


if __name__ == "__main__":
    main()
