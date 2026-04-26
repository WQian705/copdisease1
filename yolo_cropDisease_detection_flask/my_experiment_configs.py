from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DATABASE_DIR = Path(r"C:\Users\33400\Desktop\YOLO_AI\web\database")
WORKSPACE_DIR = ROOT_DIR / "my_workspace"
PREPARED_DATA_DIR = WORKSPACE_DIR / "my_prepared_datasets"
RUNS_DIR = WORKSPACE_DIR / "my_runs"
REPORTS_DIR = WORKSPACE_DIR / "my_reports"


DATASETS = {
    "apple": {
        "source_dir": DATABASE_DIR / "apple_dataset",
        "class_names": [
            "apple_black_rot",
            "apple_scab",
            "apple_cedar_rust",
            "apple_healthy",
        ],
    },
    "cotton": {
        "source_dir": DATABASE_DIR / "cotton_dataset",
        "class_names": [
            "cotton_blight",
            "cotton_curl_virus",
            "cotton_healthy",
            "cotton_wilt",
            "cotton_other_leaf_damage",
        ],
    },
    "rice": {
        "source_dir": DATABASE_DIR / "rice_dataset",
        "class_names": [
            "rice_class_0",
            "rice_class_1",
            "rice_class_2",
            "rice_class_3",
            "rice_class_4",
            "rice_class_5",
            "rice_class_6",
            "rice_class_7",
        ],
    },
}


COMMON_TRAIN_ARGS = {
    "model": "yolo11n.pt",
    "epochs": 15,
    "imgsz": 640,
    "batch": 8,
    "device": 0,
    "workers": 0,
    "project": str(RUNS_DIR),
    "exist_ok": True,
    "pretrained": True,
    "seed": 42,
    "deterministic": False,
    "verbose": True,
    "plots": True,
    "amp": True,
    "patience": 10,
    "save": True,
    "save_period": -1,
    "close_mosaic": 5,
}


TRAINING_VARIANTS = {
    "official_baseline": {
        "description": "Ultralytics official-style fine-tuning baseline",
        "train_args": {
            **COMMON_TRAIN_ARGS,
            "optimizer": "auto",
            "lr0": 0.01,
            "lrf": 0.01,
            "cos_lr": False,
            "mosaic": 1.0,
            "mixup": 0.0,
            "copy_paste": 0.0,
            "degrees": 0.0,
            "translate": 0.1,
            "scale": 0.5,
            "fliplr": 0.5,
            "hsv_h": 0.015,
            "hsv_s": 0.7,
            "hsv_v": 0.4,
        },
    },
    "optimized_a": {
        "description": "Balanced optimization with AdamW, cosine schedule and stronger regularization",
        "train_args": {
            **COMMON_TRAIN_ARGS,
            "optimizer": "AdamW",
            "lr0": 0.003,
            "lrf": 0.05,
            "cos_lr": True,
            "weight_decay": 0.0008,
            "warmup_epochs": 3.0,
            "label_smoothing": 0.01,
            "mosaic": 0.8,
            "mixup": 0.15,
            "copy_paste": 0.0,
            "degrees": 8.0,
            "translate": 0.12,
            "scale": 0.6,
            "shear": 2.0,
            "perspective": 0.0005,
            "fliplr": 0.5,
            "hsv_h": 0.02,
            "hsv_s": 0.75,
            "hsv_v": 0.45,
            "cache": "disk",
        },
    },
    "optimized_b": {
        "description": "Higher-resolution multi-scale training for small lesion sensitivity",
        "train_args": {
            **COMMON_TRAIN_ARGS,
            "imgsz": 768,
            "batch": 6,
            "optimizer": "SGD",
            "lr0": 0.008,
            "lrf": 0.08,
            "cos_lr": True,
            "momentum": 0.95,
            "weight_decay": 0.0005,
            "warmup_epochs": 2.0,
            "multi_scale": False,
            "mosaic": 0.6,
            "mixup": 0.1,
            "degrees": 5.0,
            "translate": 0.08,
            "scale": 0.7,
            "perspective": 0.0003,
            "fliplr": 0.5,
            "hsv_h": 0.018,
            "hsv_s": 0.7,
            "hsv_v": 0.4,
            "cache": False,
        },
    },
}
