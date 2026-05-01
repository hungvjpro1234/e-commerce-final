import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import get_session_factory
from app.services.chatbot import export_phase8_artifacts


def main() -> None:
    session = get_session_factory()()
    try:
        result = export_phase8_artifacts(session=session)
    finally:
        session.close()
    print(result)


if __name__ == "__main__":
    main()
