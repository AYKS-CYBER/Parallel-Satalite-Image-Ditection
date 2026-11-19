"""
test_full_pipeline.py
=====================
Automated verification script for the complete Satellite Change Detection System.
Tests image loading, sequential processing, parallel processing, visualizations,
poster generation, and report export.
"""

import os
import sys
import time

sys.path.insert(0, r"C:\Users\Asus\.gemini\antigravity\scratch\parallel-satellite-change-detection")

import image_processing as ip
import sequential_processing as seq
import parallel_processing as par
import visualization as viz
import utils
import cv2

def run_tests():
    print("=" * 60)
    print("SATELLITE CHANGE DETECTION SYSTEM - INTEGRATION TESTS")
    print("=" * 60)

    # 1. Verify Sample Dataset Loading
    samples = utils.get_available_samples()
    print(f"Available curated sample datasets: {len(samples)}")
    assert len(samples) >= 4, "Expected at least 4 sample datasets"
    for name, s in samples.items():
        print(f"  - {name}: {s['resolution']} ({s['key']})")

    # Load Urban Development
    sample_key = "Urban Expansion & Construction"
    s_info = samples[sample_key]
    b_img = utils.load_image_from_path(s_info["before"])
    a_img = utils.load_image_from_path(s_info["after"])
    print(f"\nLoaded images for '{sample_key}': shape={b_img.shape}")
    assert b_img.shape == a_img.shape, "Before and after dimensions mismatch"

    # 2. Test Sequential Processing (Tiled)
    print("\nRunning Sequential Change Detection (Tiled Single Core)...")
    t0 = time.perf_counter()
    seq_res = seq.run_sequential_tiled_detection(
        b_img, a_img,
        grid_rows=4, grid_cols=4,
        diff_mode="Deep Structural & Bilateral Analysis",
        blur_kernel=7,
        threshold_type="Otsu Automatic",
        morph_kernel=3,
        min_area=60
    )
    t_seq = seq_res["execution_time"]
    print(f"Sequential Execution Time: {t_seq:.4f}s")
    print(f"Changed Pixels (Seq): {seq_res['metrics']['changed_pixels']:,} ({seq_res['metrics']['change_percentage']:.2f}%)")
    print(f"Detected Regions (Seq): {seq_res['metrics']['region_count']}")

    # Pre-warm pool for realistic steady-state multiprocessing benchmark
    par.get_or_create_pool(4)

    # 3. Test Parallel Processing with 4 workers, 4x4 grid (16 tiles)
    print("\nRunning Parallel Change Detection (4 workers, 4x4 grid)...")
    par_res = par.run_parallel_change_detection(
        b_img, a_img,
        grid_rows=4, grid_cols=4,
        num_processes=4,
        diff_mode="Deep Structural & Bilateral Analysis",
        blur_kernel=7,
        threshold_type="Otsu Automatic",
        morph_kernel=3,
        min_area=60
    )
    t_par = par_res["execution_time"]
    speedup = t_seq / t_par if t_par > 0 else 1.0
    eff = (speedup / 4) * 100
    print(f"Parallel Execution Time: {t_par:.4f}s (Pure compute: {par_res['pure_compute_time']:.4f}s)")
    print(f"Changed Pixels (Par): {par_res['metrics']['changed_pixels']:,} ({par_res['metrics']['change_percentage']:.2f}%)")
    print(f"Detected Regions (Par): {par_res['metrics']['region_count']}")
    print(f"Speedup: {speedup:.2f}x | Parallel Efficiency: {eff:.1f}%")

    # 4. Test Visualizations & Overlays
    print("\nGenerating Visualizations...")
    diff_heatmap = ip.generate_diff_heatmap(par_res["diff_map"])
    assert diff_heatmap.shape == b_img.shape, "Heatmap shape mismatch"

    overlay_img = ip.generate_change_overlay(
        a_img, par_res["binary_mask"],
        overlay_color=(255, 30, 30),
        alpha=0.45,
        draw_bounding_boxes=True,
        draw_contours=True,
        min_box_area=60
    )
    assert overlay_img.shape == b_img.shape, "Overlay shape mismatch"
    print("Change overlay created successfully.")

    tile_grid_vis = ip.draw_tile_grid_overlay(a_img, par_res["tile_info"])
    assert tile_grid_vis.shape == b_img.shape, "Grid overlay shape mismatch"
    print("Tile grid overlay created successfully.")

    # 5. Test 5-Panel Poster Generation
    print("\nGenerating 5-Panel Geospatial Poster...")
    poster = viz.generate_composite_report_image(
        before_img=b_img,
        after_img=a_img,
        diff_heatmap=diff_heatmap,
        binary_mask=par_res["binary_mask"],
        overlay_img=overlay_img,
        metrics=par_res["metrics"],
        speedup=speedup,
        efficiency=eff,
        seq_time=t_seq,
        par_time=t_par,
        num_processes=4
    )
    poster_path = r"C:\Users\Asus\.gemini\antigravity\scratch\parallel-satellite-change-detection\sample_poster.png"
    cv2.imwrite(poster_path, cv2.cvtColor(poster, cv2.COLOR_RGB2BGR))
    print(f"Saved sample poster to: {poster_path} (size: {poster.shape})")

    # 6. Test Markdown Report Generation
    print("\nGenerating Technical Report...")
    report_md = utils.generate_markdown_report(
        dataset_name=sample_key,
        img_shape=b_img.shape[:2],
        diff_mode="Deep Structural & Bilateral Analysis",
        threshold_type="Otsu Automatic",
        seq_res=seq_res,
        par_res=par_res,
        speedup=speedup,
        efficiency=eff
    )
    report_path = r"C:\Users\Asus\.gemini\antigravity\scratch\parallel-satellite-change-detection\sample_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Saved sample report to: {report_path}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
