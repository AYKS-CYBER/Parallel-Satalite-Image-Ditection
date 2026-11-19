"""
utils.py
========
Utility functions for dataset loading, report generation, and file exporting.
"""

import os
import io
import json
import time
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Tuple, Optional, List


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")


SAMPLE_DATASETS = {
    "Urban Expansion & Construction": {
        "key": "urban_development",
        "description": "Newly constructed logistics warehouses, residential subdivisions, asphalt highways, and cleared construction ground.",
        "before": os.path.join(SAMPLES_DIR, "urban_development_before.png"),
        "after": os.path.join(SAMPLES_DIR, "urban_development_after.png"),
        "resolution": "1600 x 1600",
        "expected_changes": "Industrial warehouses, residential roofs, road network"
    },
    "Tropical Rainforest Deforestation": {
        "key": "deforestation",
        "description": "Massive canopy clear-cutting, bare soil conversion, and branching logging fishbone tracks in ancient rainforest.",
        "before": os.path.join(SAMPLES_DIR, "deforestation_before.png"),
        "after": os.path.join(SAMPLES_DIR, "deforestation_after.png"),
        "resolution": "1600 x 1600",
        "expected_changes": "Clear-cut forest plots, dirt access corridors, exposed earth"
    },
    "Highway & Interchange Expansion": {
        "key": "infrastructure",
        "description": "New multi-lane high-speed expressway, cloverleaf interchange ramps, and logistics facilities.",
        "before": os.path.join(SAMPLES_DIR, "infrastructure_before.png"),
        "after": os.path.join(SAMPLES_DIR, "infrastructure_after.png"),
        "resolution": "1600 x 1600",
        "expected_changes": "Expressway pavement, cloverleaf ramps, distribution depot"
    },
    "Reservoir Retreat & Drought Dynamics": {
        "key": "reservoir_drought",
        "description": "Severe freshwater reservoir retreat, exposed lakebed mudflats, and cracked sediment.",
        "before": os.path.join(SAMPLES_DIR, "reservoir_drought_before.png"),
        "after": os.path.join(SAMPLES_DIR, "reservoir_drought_after.png"),
        "resolution": "1600 x 1600",
        "expected_changes": "Receding shoreline, dry lakebed silt, wetland loss"
    }
}


def get_available_samples() -> Dict[str, Dict[str, Any]]:
    """Return dictionary of available sample satellite datasets."""
    available = {}
    for name, info in SAMPLE_DATASETS.items():
        if os.path.exists(info["before"]) and os.path.exists(info["after"]):
            available[name] = info
    return available


def load_image_from_path(path: str) -> np.ndarray:
    """Load image from disk and return RGB numpy array."""
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        raise FileNotFoundError(f"Could not load image from {path}")
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def load_image_from_upload(uploaded_file) -> np.ndarray:
    """Read Streamlit uploaded file buffer and convert to RGB numpy array."""
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img_bgr is None:
        # Fallback to PIL
        uploaded_file.seek(0)
        pil_img = Image.open(uploaded_file).convert("RGB")
        return np.array(pil_img)
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def numpy_to_download_bytes(img_arr: np.ndarray, format: str = "PNG") -> bytes:
    """Convert numpy array image to in-memory bytes for Streamlit download."""
    pil_img = Image.fromarray(img_arr)
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()


def generate_markdown_report(
    dataset_name: str,
    img_shape: Tuple[int, int],
    diff_mode: str,
    threshold_type: str,
    seq_res: Dict[str, Any],
    par_res: Dict[str, Any],
    speedup: float,
    efficiency: float
) -> str:
    """
    Generate a comprehensive technical executive report in Markdown.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    h, w = img_shape
    total_pixels = h * w
    metrics = par_res["metrics"]

    report = f"""# SATELLITE IMAGE CHANGE DETECTION & PARALLEL COMPUTING REPORT
**System:** Satellite Change Detection System (AI-Assisted Geospatial Analysis)  
**Execution Timestamp:** {now_str}  
**Image Resolution:** {w} x {h} pixels ({total_pixels:,} total pixels)  
**Dataset / Subject:** {dataset_name}  

---

## 1. Executive Performance Summary

| Metric | Sequential Processing | Parallel Processing | Performance Delta |
| :--- | :--- | :--- | :--- |
| **Execution Architecture** | Single CPU Process | Multiprocessing Pool | **{par_res['num_processes']} Worker Cores** |
| **Spatial Decomposition** | Monolithic / Full Image | {par_res['grid'][0]} x {par_res['grid'][1]} Grid | **{par_res['total_tiles']} Independent Tiles** |
| **Execution Time** | **{seq_res['execution_time']:.4f} s** | **{par_res['execution_time']:.4f} s** | **{max(0, seq_res['execution_time'] - par_res['execution_time']):.4f} s Saved** |
| **Speedup Factor** | 1.00x (Baseline) | **{speedup:.2f}x** | **{((speedup - 1.0) * 100):.1f}% Faster** |
| **Parallel Efficiency** | 100.0% | **{efficiency:.1f}%** | Hardware Utilization |

### Performance Evaluation
{"Parallel computing significantly reduced the execution time." if speedup > 1.0 else "Sequential execution was faster due to process dispatch overhead on small workload."}
- **Amdahl's Law Speedup:** Measured at **{speedup:.2f}x** across **{par_res['num_processes']} CPU cores**.
- **Efficiency:** Achieved **{efficiency:.1f}%** parallel efficiency.

---

## 2. Geospatial Change Detection Analytics

| Geospatial Parameter | Value | Description |
| :--- | :--- | :--- |
| **Total Surface Changed** | **{metrics.get('change_percentage', 0.0):.2f}%** | Percentage of geographical ground surface modified |
| **Changed Pixels** | **{metrics.get('changed_pixels', 0):,} px** | Pixel count exceeding significance threshold |
| **Discrete Change Clusters** | **{metrics.get('region_count', 0):,} regions** | Distinct contiguous building/road/land parcels |
| **Mean Parcel Area** | **{metrics.get('mean_region_size', 0.0):.1f} px²** | Average spatial extent per detected cluster |

---

## 3. Algorithm & Processing Configuration

- **Difference Mode:** `{diff_mode}`
- **Thresholding Strategy:** `{threshold_type}`
- **Tile Partitioning:** `{par_res['grid'][0]} rows x {par_res['grid'][1]} cols` ({par_res['total_tiles']} non-overlapping spatial tiles)
- **Edge Handling:** Exact integer linear coordinate interpolation without seam artifacts or overlap gaps.

---

## 4. System Capabilities & Methodological Disclosures

> **Geospatial Analysis Note:**  
> This system performs pixel differencing, structural gradient comparison, and morphological clustering between co-registered satellite images.  
> The system detects visual, spectral, and radiometric deviations across time periods. It flags potential construction, vegetation loss, and water dynamics without asserting definitive semantic object class labels unless paired with deep neural segmentation or multi-spectral band indexing (e.g., NDVI/NDWI).

---
*Report automatically generated by the Satellite Change Detection System.*
"""
    return report


def create_satellite_timelapse_gif(
    img_before: np.ndarray,
    img_after: np.ndarray,
    img_overlay: np.ndarray,
    diff_heatmap: Optional[np.ndarray] = None,
    target_size: Tuple[int, int] = (640, 640),
    duration_ms: int = 1000
) -> bytes:
    """
    Generates a high-quality multi-frame looping GIF cycling through:
    1. T1: Before Satellite Scene
    2. T2: After Satellite Scene
    3. T2 + Detected Changes (Red Overlays & Bounding Boxes)
    4. Difference Thermal Heatmap (Optional)
    """
    frames = []

    def annotate_frame(img_rgb: np.ndarray, title: str, tag: str, tag_color: Tuple[int, int, int]) -> Image.Image:
        resized = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_AREA)
        header_h = 44
        canvas = np.zeros((target_size[1] + header_h, target_size[0], 3), dtype=np.uint8)
        canvas[:header_h, :] = (15, 23, 42)  # Dark slate navy
        canvas[header_h:, :] = resized

        # Add text overlay
        cv2.putText(canvas, title, (14, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, tag, (target_size[0] - 145, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, tag_color, 2, cv2.LINE_AA)

        # Bottom subtle branding bar
        cv2.putText(canvas, "PARALLEL SATELLITE CHANGE DETECTION", (14, target_size[1] + header_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1, cv2.LINE_AA)

        return Image.fromarray(canvas)

    frames.append(annotate_frame(img_before, "T1: Prior Satellite Acquisition", "[BEFORE]", (0, 245, 212)))
    frames.append(annotate_frame(img_after, "T2: Recent Satellite Acquisition", "[AFTER]", (255, 209, 102)))
    frames.append(annotate_frame(img_overlay, "T2: Detected Structural Changes", "[CHANGES]", (239, 71, 111)))
    if diff_heatmap is not None:
        frames.append(annotate_frame(diff_heatmap, "Diff: Absolute Magnitude Heatmap", "[HEATMAP]", (6, 214, 160)))

    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    return buf.getvalue()
