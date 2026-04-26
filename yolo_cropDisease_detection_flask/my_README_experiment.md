# my_YOLO crop disease experiment

This folder contains a standalone experiment pipeline for thesis use.

Files:
- `my_prepare_datasets.py`: converts polygon and bbox labels to unified YOLO detection labels.
- `my_experiment_configs.py`: central configuration for datasets and training variants.
- `my_train_models.py`: trains and tests the three crops with three training strategies.
- `my_collect_results.py`: aggregates metrics, model size, FLOPs and speed, then exports plots.
- `my_run_all.py`: one-click full pipeline runner.

Outputs:
- `my_workspace/my_prepared_datasets`: converted datasets and `my_*.yaml`.
- `my_workspace/my_runs`: training and test runs.
- `my_workspace/my_reports`: CSV, JSON and performance comparison figures.

Notes:
- All code, generated datasets, runs, plots and reports are prefixed with `my_`.
- Rice class names were not explicitly present in the source dataset metadata, so they are retained as `rice_class_0` to `rice_class_7`.
