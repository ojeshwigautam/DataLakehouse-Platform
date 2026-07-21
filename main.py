import sys

from src.pipeline.etl_pipeline import run_pipeline


def main():
    success = run_pipeline()
    if success:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
