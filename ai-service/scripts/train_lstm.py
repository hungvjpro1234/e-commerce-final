import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.ml.train_lstm import train_and_evaluate_lstm


def main() -> None:
    result = train_and_evaluate_lstm()
    print(result["message"])
    print(f"Summary: {result['summary_path']}")
    print(f"Report: {result['report_path']}")
    print(f"Model: {result['model_path']}")


if __name__ == "__main__":
    main()
