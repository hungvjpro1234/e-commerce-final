import os
import sys
from pathlib import Path


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

os.environ["AI_DB_ENGINE"] = "sqlite"
os.environ["AI_DB_NAME"] = str(Path(__file__).with_name("phase2-test.db"))
