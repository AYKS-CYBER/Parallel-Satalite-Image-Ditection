"""
sequential_processing.py
========================
Sequential (single-process) implementation of satellite image change detection.
Measures execution time accurately with detailed stage breakdown.
"""

import time
import numpy as np
import cv2
from typing import Dict, Any, Tuple
import image_processing as ip


def run_sequential_change_detection(
    before_img: np.ndarray,
    after_img: np.ndarray,
    diff_mode: str = "Deep Structural & Bilateral Analysis",
    blur_kernel: int = 5,
    threshold_type: str = "Otsu Automatic",
    manual_threshold: int = 35,
    morph_kernel: int = 3,
    min_area: int = 40,
    progress_callback = None
) -> Dict[str, Any]:
    """
    Executes change detection sequentially using a single CPU process.
    """
    if progress_callback:
        progress_callback(0.1, "Sequential: Computing difference map...")

    start_total = time.perf_counter()

    # Stage 1: Difference Map Computation
    t0 = time.perf_counter()
    diff_map = ip.compute_difference_map(
        before_img, after_img, diff_mode=diff_mode, blur_kernel=blur_kernel
    )
    t_diff = time.perf_counter() - t0

    if progress_callback:
        progress_callback(0.6, "Sequential: Applying thresholding...")

    # Stage 2: Thresholding
    t1 = time.perf_counter()
    raw_mask, thresh_val = ip.threshold_difference(
        diff_map, threshold_type=threshold_type, manual_threshold=manual_threshold
    )
    t_thresh = time.perf_counter() - t1

    if progress_callback:
        progress_callback(0.8, "Sequential: Morphological filtering & region extraction...")

    # Stage 3: Morphological Cleanup & Filtering
    t2 = time.perf_counter()
    clean_mask = ip.apply_morphological_cleanup(
        raw_mask, kernel_size=morph_kernel, min_contour_area=min_area
    )
    t_morph = time.perf_counter() - t2

    total_time = time.perf_counter() - start_total

    # Metrics
    metrics = ip.extract_change_metrics(clean_mask, min_area=min_area)

    if progress_callback:
        progress_callback(1.0, "Sequential processing complete.")

    return {
        "diff_map": diff_map,
        "binary_mask": clean_mask,
        "raw_mask": raw_mask,
        "threshold_val": thresh_val,
        "execution_time": total_time,
        "stage_timings": {
            "difference_time": t_diff,
            "threshold_time": t_thresh,
            "cleanup_time": t_morph
        },
        "metrics": metrics,
        "num_processes": 1,
        "mode": "Sequential Full-Frame"
    }


def run_sequential_tiled_detection(
    before_img: np.ndarray,
    after_img: np.ndarray,
    grid_rows: int = 4,
    grid_cols: int = 4,
    diff_mode: str = "Deep Structural & Bilateral Analysis",
    blur_kernel: int = 5,
    threshold_type: str = "Otsu Automatic",
    manual_threshold: int = 35,
    morph_kernel: int = 3,
    min_area: int = 40,
    progress_callback = None
) -> Dict[str, Any]:
    """
    Executes change detection sequentially across individual tiles on a single core.
    Serves as an exact algorithmic baseline counterpart to parallel tile multiprocessing.
    """
    h, w = before_img.shape[:2]
    start_total = time.perf_counter()

    # Pre-calibrate threshold if Otsu
    effective_thresh = manual_threshold
    if threshold_type == "Otsu Automatic":
        from parallel_processing import calibrate_global_otsu_threshold
        effective_thresh = calibrate_global_otsu_threshold(before_img, after_img, diff_mode, blur_kernel)

    diff_map = np.zeros((h, w), dtype=np.uint8)
    clean_mask = np.zeros((h, w), dtype=np.uint8)

    row_bounds = np.linspace(0, h, grid_rows + 1, dtype=int)
    col_bounds = np.linspace(0, w, grid_cols + 1, dtype=int)

    total_tiles = grid_rows * grid_cols
    tile_info_list = []
    tile_id = 0

    for r in range(grid_rows):
        y1, y2 = int(row_bounds[r]), int(row_bounds[r + 1])
        for c in range(grid_cols):
            x1, x2 = int(col_bounds[c]), int(col_bounds[c + 1])

            tile_b = before_img[y1:y2, x1:x2]
            tile_a = after_img[y1:y2, x1:x2]

            d_tile, m_tile, cnt = ip.execute_tile_pipeline(
                tile_b, tile_a, diff_mode, blur_kernel,
                "Manual Threshold" if threshold_type == "Otsu Automatic" else threshold_type,
                effective_thresh, morph_kernel, min_area
            )

            diff_map[y1:y2, x1:x2] = d_tile
            clean_mask[y1:y2, x1:x2] = m_tile

            tile_info_list.append({
                "tile_id": tile_id,
                "bbox": (y1, y2, x1, x2),
                "changed_count": cnt
            })
            tile_id += 1

            if progress_callback:
                progress_callback(tile_id / total_tiles, f"Sequential Tile {tile_id}/{total_tiles}...")

    total_time = time.perf_counter() - start_total
    metrics = ip.extract_change_metrics(clean_mask, min_area=min_area)

    return {
        "diff_map": diff_map,
        "binary_mask": clean_mask,
        "execution_time": total_time,
        "metrics": metrics,
        "num_processes": 1,
        "grid": (grid_rows, grid_cols),
        "total_tiles": total_tiles,
        "tile_info": tile_info_list,
        "mode": "Sequential Tiled (Single Process)"
    }
