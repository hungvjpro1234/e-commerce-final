import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.rag import rebuild_rag_index


if __name__ == "__main__":
    result = rebuild_rag_index()
    print(result.model_dump_json(indent=2))
