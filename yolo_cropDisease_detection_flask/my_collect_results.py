from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from ultralytics import YOLO
from ultralytics.utils.torch_utils import get_flops

from my_experiment_configs import REPORTS_DIR, RUNS_DIR, TRAINING_VARIANTS


def parse_model_info(model_path: Path) -> tuple[int, float]:
    model = YOLO(str(model_path))
    params = sum(p.numel() for p in model.model.parameters())
    gflops = float(get_flops(model.model, imgsz=640))
    return params, gflops


def load_best_metrics(test_run_dir: Path) -> dict:
    metrics_json = test_run_dir / "my_test_metrics.json"
    if metrics_json.exists():
        payload = json.loads(metrics_json.read_text(encoding="utf-8"))
        row = dict(payload.get("results_dict", {}))
        speed = payload.get("speed", {})
        row["speed/preprocess"] = speed.get("preprocess", -1.0)
        row["speed/inference"] = speed.get("inference", -1.0)
        row["speed/loss"] = speed.get("loss", -1.0)
        row["speed/postprocess"] = speed.get("postprocess", -1.0)
        return row
    csv_path = test_run_dir / "results.csv"
    df = pd.read_csv(csv_path)
    row = df.iloc[-1].to_dict()
    return {k.strip(): v for k, v in row.items()}


def find_test_run_dir(run_name: str) -> Path:
    candidates = sorted(RUNS_DIR.glob(f"{run_name}_test*"))
    if not candidates:
        raise FileNotFoundError(f"Missing test run for {run_name}")
    return candidates[-1]


def collect_rows() -> list[dict]:
    rows = []
    for variant_name, variant in TRAINING_VARIANTS.items():
        for train_run_dir in sorted(RUNS_DIR.glob(f"my_*_{variant_name}")):
            if not train_run_dir.is_dir():
                continue
            parts = train_run_dir.name.split("_")
            crop_name = parts[1]
            test_run_dir = find_test_run_dir(train_run_dir.name)
            best_model = train_run_dir / "weights" / "best.pt"
            args_path = train_run_dir / "args.yaml"
            results_path = train_run_dir / "results.csv"
            if not best_model.exists() or not results_path.exists():
                continue

            train_df = pd.read_csv(results_path)
            best_epoch_row = train_df.iloc[train_df["metrics/mAP50-95(B)"].idxmax()]
            test_metrics = load_best_metrics(test_run_dir)
            params, gflops = parse_model_info(best_model)
            fitness = float(
                0.1 * best_epoch_row["metrics/mAP50(B)"] + 0.9 * best_epoch_row["metrics/mAP50-95(B)"]
            )

            rows.append(
                {
                    "crop": crop_name,
                    "variant": variant_name,
                    "description": variant["description"],
                    "train_run_dir": str(train_run_dir),
                    "test_run_dir": str(test_run_dir),
                    "best_model": str(best_model),
                    "epochs_ran": int(train_df["epoch"].max() + 1),
                    "best_train_epoch": int(best_epoch_row["epoch"]),
                    "train_precision_B": float(best_epoch_row["metrics/precision(B)"]),
                    "train_recall_B": float(best_epoch_row["metrics/recall(B)"]),
                    "train_map50_B": float(best_epoch_row["metrics/mAP50(B)"]),
                    "train_map50_95_B": float(best_epoch_row["metrics/mAP50-95(B)"]),
                    "test_precision_B": float(test_metrics["metrics/precision(B)"]),
                    "test_recall_B": float(test_metrics["metrics/recall(B)"]),
                    "test_map50_B": float(test_metrics["metrics/mAP50(B)"]),
                    "test_map50_95_B": float(test_metrics["metrics/mAP50-95(B)"]),
                    "fitness": fitness,
                    "train_box_loss": float(best_epoch_row["train/box_loss"]),
                    "train_cls_loss": float(best_epoch_row["train/cls_loss"]),
                    "train_dfl_loss": float(best_epoch_row["train/dfl_loss"]),
                    "val_box_loss": float(best_epoch_row["val/box_loss"]),
                    "val_cls_loss": float(best_epoch_row["val/cls_loss"]),
                    "val_dfl_loss": float(best_epoch_row["val/dfl_loss"]),
                    "preprocess_ms": float(test_metrics["speed/preprocess"]),
                    "inference_ms": float(test_metrics["speed/inference"]),
                    "loss_ms": float(test_metrics["speed/loss"]),
                    "postprocess_ms": float(test_metrics["speed/postprocess"]),
                    "params": params,
                    "gflops": gflops,
                    "args_yaml": str(args_path),
                }
            )
    return rows


def save_csv(rows: list[dict]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "my_experiment_summary.csv"
    if not rows:
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["crop", "variant"])
        return csv_path
    df = pd.DataFrame(rows).sort_values(["crop", "variant"])
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def save_json(rows: list[dict]) -> Path:
    json_path = REPORTS_DIR / "my_experiment_summary.json"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return json_path


def save_plots(rows: list[dict]) -> list[Path]:
    df = pd.DataFrame(rows)
    output_paths = []
    if df.empty:
        return output_paths

    metric_map = {
        "test_map50_B": "mAP50",
        "test_map50_95_B": "mAP50-95",
        "test_precision_B": "Precision",
        "test_recall_B": "Recall",
        "inference_ms": "Inference(ms/img)",
    }

    for crop_name, crop_df in df.groupby("crop"):
        fig, axes = plt.subplots(1, len(metric_map), figsize=(20, 4))
        for ax, (column, title) in zip(axes, metric_map.items()):
            ordered = crop_df.sort_values("variant")
            ax.bar(ordered["variant"], ordered[column], color=["#4e79a7", "#f28e2b", "#59a14f"])
            ax.set_title(f"{crop_name} {title}")
            ax.tick_params(axis="x", rotation=20)
        fig.tight_layout()
        plot_path = REPORTS_DIR / f"my_{crop_name}_comparison.png"
        fig.savefig(plot_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        output_paths.append(plot_path)

    mean_df = (
        df.groupby("variant")[["test_map50_B", "test_map50_95_B", "test_precision_B", "test_recall_B"]]
        .mean()
        .reset_index()
    )
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, column in zip(axes, ["test_map50_B", "test_map50_95_B", "test_precision_B", "test_recall_B"]):
        ax.bar(mean_df["variant"], mean_df[column], color=["#4e79a7", "#f28e2b", "#59a14f"])
        ax.set_title(f"overall {column}")
        ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    overall_path = REPORTS_DIR / "my_overall_comparison.png"
    fig.savefig(overall_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    output_paths.append(overall_path)
    return output_paths


def main() -> None:
    rows = collect_rows()
    csv_path = save_csv(rows)
    json_path = save_json(rows)
    plot_paths = save_plots(rows)
    print(f"[summary_csv] {csv_path}")
    print(f"[summary_json] {json_path}")
    for path in plot_paths:
        print(f"[plot] {path}")


if __name__ == "__main__":
    main()
