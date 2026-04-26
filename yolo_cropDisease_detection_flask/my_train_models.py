from __future__ import annotations

import argparse
import json
from pathlib import Path

from ultralytics import YOLO

from my_experiment_configs import DATASETS, PREPARED_DATA_DIR, RUNS_DIR, TRAINING_VARIANTS


def to_builtin(value):
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_builtin(v) for v in value]
    if isinstance(value, tuple):
        return [to_builtin(v) for v in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def get_data_yaml(crop_name: str) -> Path:
    return PREPARED_DATA_DIR / f"my_{crop_name}_dataset_detect" / f"my_{crop_name}_data.yaml"


def train_one(crop_name: str, variant_name: str, epochs_override: int | None = None) -> dict:
    data_yaml = get_data_yaml(crop_name)
    if not data_yaml.exists():
        raise FileNotFoundError(f"Prepared dataset not found: {data_yaml}")

    variant = TRAINING_VARIANTS[variant_name]
    train_args = dict(variant["train_args"])
    if epochs_override is not None:
        train_args["epochs"] = epochs_override
    run_name = f"my_{crop_name}_{variant_name}"
    model_path = train_args.pop("model")
    model = YOLO(model_path)

    print(f"[train] crop={crop_name}, variant={variant_name}, run={run_name}")
    results = model.train(
        data=str(data_yaml),
        name=run_name,
        **train_args,
    )

    best_model = Path(results.save_dir) / "weights" / "best.pt"
    best_model_runner = YOLO(str(best_model))

    metrics = best_model_runner.val(
        data=str(data_yaml),
        split="test",
        name=f"{run_name}_test",
        project=str(RUNS_DIR),
        imgsz=train_args["imgsz"],
        batch=train_args["batch"],
        device=train_args["device"],
        plots=True,
    )
    test_metrics_payload = {
        "results_dict": to_builtin(metrics.results_dict),
        "speed": to_builtin(metrics.speed),
        "class_summary": to_builtin(metrics.summary()),
        "save_dir": str(metrics.save_dir),
    }
    test_metrics_path = Path(metrics.save_dir) / "my_test_metrics.json"
    test_metrics_path.write_text(json.dumps(test_metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "crop": crop_name,
        "variant": variant_name,
        "description": variant["description"],
        "train_run_dir": str(results.save_dir),
        "test_run_dir": str(metrics.save_dir),
        "best_model": str(best_model),
        "test_metrics_json": str(test_metrics_path),
    }
    summary_path = Path(results.save_dir) / "my_run_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--crop", choices=list(DATASETS.keys()) + ["all"], default="all")
    parser.add_argument("--variant", choices=list(TRAINING_VARIANTS.keys()) + ["all"], default="all")
    parser.add_argument("--epochs", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crops = list(DATASETS.keys()) if args.crop == "all" else [args.crop]
    variants = list(TRAINING_VARIANTS.keys()) if args.variant == "all" else [args.variant]
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    all_runs = []
    for crop_name in crops:
        for variant_name in variants:
            all_runs.append(train_one(crop_name, variant_name, epochs_override=args.epochs))

    print("\n[finished]")
    for item in all_runs:
        print(json.dumps(item, ensure_ascii=False))


if __name__ == "__main__":
    main()
