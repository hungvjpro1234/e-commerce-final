import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import get_session_factory, init_db
from app.services.behavior import export_behavior_artifacts


def main() -> None:
    init_db()
    session = get_session_factory()()
    try:
        result = export_behavior_artifacts(session)
    finally:
        session.close()

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
