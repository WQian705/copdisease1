from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run_step(script_name: str, *args: str) -> None:
    command = [sys.executable, str(ROOT / script_name), *args]
    print(f"[run] {' '.join(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    run_step("my_prepare_datasets.py")
    run_step("my_train_models.py", "--crop", "all", "--variant", "all")
    run_step("my_collect_results.py")


if __name__ == "__main__":
    main()
