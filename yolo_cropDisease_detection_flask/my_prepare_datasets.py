from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from my_experiment_configs import DATASETS, PREPARED_DATA_DIR


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def polygon_to_bbox(values: list[float]) -> tuple[float, float, float, float]:
    xs = values[0::2]
    ys = values[1::2]
    min_x = max(0.0, min(xs))
    max_x = min(1.0, max(xs))
    min_y = max(0.0, min(ys))
    max_y = min(1.0, max(ys))
    x_center = (min_x + max_x) / 2.0
    y_center = (min_y + max_y) / 2.0
    width = max_x - min_x
    height = max_y - min_y
    return x_center, y_center, width, height


def convert_label_line(line: str) -> str | None:
    parts = line.strip().split()
    if not parts:
        return None
    cls_id = int(float(parts[0]))
    coords = [float(x) for x in parts[1:]]
    if len(coords) < 4:
        return None
    if len(coords) == 4:
        x_center, y_center, width, height = coords
    else:
        x_center, y_center, width, height = polygon_to_bbox(coords)
    width = min(max(width, 1e-6), 1.0)
    height = min(max(height, 1e-6), 1.0)
    x_center = min(max(x_center, 0.0), 1.0)
    y_center = min(max(y_center, 0.0), 1.0)
    return f"{cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def copy_and_convert_split(src_split_dir: Path, dst_split_dir: Path) -> dict[str, int]:
    stats = {
        "images": 0,
        "labels": 0,
        "polygon_labels": 0,
        "bbox_labels": 0,
        "empty_labels": 0,
    }
    image_src = src_split_dir / "images"
    label_src = src_split_dir / "labels"
    image_dst = dst_split_dir / "images"
    label_dst = dst_split_dir / "labels"
    ensure_dir(image_dst)
    ensure_dir(label_dst)

    for image_path in sorted(image_src.glob("*")):
        if image_path.is_file():
            shutil.copy2(image_path, image_dst / image_path.name)
            stats["images"] += 1

    for label_path in sorted(label_src.glob("*.txt")):
        converted_lines = []
        original_lines = label_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in original_lines:
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) == 5:
                stats["bbox_labels"] += 1
            elif len(parts) > 5:
                stats["polygon_labels"] += 1
            new_line = convert_label_line(line)
            if new_line is not None:
                converted_lines.append(new_line)
        if not converted_lines:
            stats["empty_labels"] += 1
        (label_dst / label_path.name).write_text("\n".join(converted_lines), encoding="utf-8")
        stats["labels"] += 1
    return stats


def prepare_dataset(crop_name: str, source_dir: Path, class_names: list[str]) -> dict:
    prepared_dir = PREPARED_DATA_DIR / f"my_{crop_name}_dataset_detect"
    if prepared_dir.exists():
        shutil.rmtree(prepared_dir)
    ensure_dir(prepared_dir)

    summary = {"crop": crop_name, "prepared_dir": str(prepared_dir), "splits": {}}
    for split in ["train", "valid", "test"]:
        summary["splits"][split] = copy_and_convert_split(source_dir / split, prepared_dir / split)

    data_yaml = {
        "path": str(prepared_dir),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": {idx: name for idx, name in enumerate(class_names)},
        "nc": len(class_names),
    }
    yaml_path = prepared_dir / f"my_{crop_name}_data.yaml"
    yaml_path.write_text(yaml.safe_dump(data_yaml, sort_keys=False, allow_unicode=False), encoding="utf-8")
    summary["data_yaml"] = str(yaml_path)
    return summary


def main() -> None:
    ensure_dir(PREPARED_DATA_DIR)
    all_summaries = []
    for crop_name, dataset_info in DATASETS.items():
        summary = prepare_dataset(
            crop_name=crop_name,
            source_dir=dataset_info["source_dir"],
            class_names=dataset_info["class_names"],
        )
        all_summaries.append(summary)
        print(f"[prepared] {crop_name}")
        print(f"  data_yaml: {summary['data_yaml']}")
        for split, split_stats in summary["splits"].items():
            print(f"  {split}: {split_stats}")


if __name__ == "__main__":
    main()
