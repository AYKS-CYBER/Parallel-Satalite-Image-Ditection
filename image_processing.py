"""
image_processing.py
===================
Satellite Image Preprocessing, Difference Detection, and Morphological Analysis.
Designed for high accuracy, robust edge handling, and multiprocessing tile workers.
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any, Optional


def resize_to_match(img1: np.ndarray, img2: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ensure both satellite images have identical dimensions (H, W).
    If target_size (W, H) is provided, resize both to target_size.
    Otherwise, resize img2 to match img1 dimensions.
    """
    if target_size is not None:
        w, h = target_size
        r1 = cv2.resize(img1, (w, h), interpolation=cv2.INTER_AREA if (img1.shape[1] > w) else cv2.INTER_CUBIC)
        r2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA if (img2.shape[1] > w) else cv2.INTER_CUBIC)
        return r1, r2

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    if (h1, w1) == (h2, w2):
        return img1, img2

    r2 = cv2.resize(img2, (w1, h1), interpolation=cv2.INTER_LINEAR)
    return img1, r2


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convert RGB/BGR/RGBA image to single-channel uint8 grayscale."""
    if len(img.shape) == 2:
        return img
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def align_images_orb(img_ref: np.ndarray, img_to_align: np.ndarray, max_features: int = 1500) -> Tuple[np.ndarray, bool, float]:
    """
    Align img_to_align to img_ref using ORB feature detection and RANSAC homography.
    Returns:
        (aligned_image, success_boolean, inlier_ratio)
    """
    gray_ref = to_grayscale(img_ref)
    gray_align = to_grayscale(img_to_align)

    orb = cv2.ORB_create(nfeatures=max_features)
    kp1, des1 = orb.detectAndCompute(gray_ref, None)
    kp2, des2 = orb.detectAndCompute(gray_align, None)

    if des1 is None or des2 is None or len(kp1) < 8 or len(kp2) < 8:
        return img_to_align, False, 0.0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    num_good = max(10, int(len(matches) * 0.35))
    good_matches = matches[:num_good]

    if len(good_matches) < 8:
        return img_to_align, False, 0.0

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    homography, inliers = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

    if homography is None:
        return img_to_align, False, 0.0

    inlier_ratio = float(np.sum(inliers)) / float(len(inliers)) if inliers is not None else 0.0
    h, w = img_ref.shape[:2]
    aligned = cv2.warpPerspective(img_to_align, homography, (w, h), borderMode=cv2.BORDER_REFLECT)
    return aligned, True, inlier_ratio


def compute_difference_map(
    before_img: np.ndarray,
    after_img: np.ndarray,
    diff_mode: str = "Deep Structural & Bilateral Analysis",
    blur_kernel: int = 5
) -> np.ndarray:
    """
    Compute pixel difference map between before and after satellite images.
    Modes:
      1. 'Deep Structural & Bilateral Analysis':
         Edge-preserving Bilateral Filter + Multi-channel color diff + Sobel gradient magnitude diff.
         Highly realistic for satellite pipelines, compute-intensive, showcases true parallel scaling.
      2. 'Color-Aware Absolute Difference':
         Gaussian blur + RGB multi-channel mean absolute difference.
      3. 'Structural Edge Difference':
         Gaussian blur + Laplacian structural edge difference.
      4. 'Grayscale Difference':
         Grayscale absdiff.
    """
    k = blur_kernel if blur_kernel % 2 != 0 else blur_kernel + 1

    if diff_mode == "Deep Structural & Bilateral Analysis":
        # Bilateral filtering: preserves building/road borders while smoothing radiometric texture
        d = max(5, k)
        b_filt = cv2.bilateralFilter(before_img, d=d, sigmaColor=75, sigmaSpace=75)
        a_filt = cv2.bilateralFilter(after_img, d=d, sigmaColor=75, sigmaSpace=75)

        # 1. Color diff
        diff_col = cv2.absdiff(b_filt, a_filt)
        if len(diff_col.shape) == 3:
            diff_col_mag = np.mean(diff_col, axis=2).astype(np.uint8)
        else:
            diff_col_mag = diff_col

        # 2. Structural gradient diff
        g_b = to_grayscale(b_filt)
        g_a = to_grayscale(a_filt)

        gx_b = cv2.Sobel(g_b, cv2.CV_32F, 1, 0, ksize=3)
        gy_b = cv2.Sobel(g_b, cv2.CV_32F, 0, 1, ksize=3)
        mag_b = cv2.magnitude(gx_b, gy_b)

        gx_a = cv2.Sobel(g_a, cv2.CV_32F, 1, 0, ksize=3)
        gy_a = cv2.Sobel(g_a, cv2.CV_32F, 0, 1, ksize=3)
        mag_a = cv2.magnitude(gx_a, gy_a)

        edge_diff = cv2.absdiff(mag_b, mag_a)
        edge_diff = cv2.normalize(edge_diff, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Weighted blend: 60% color shift, 40% structural geometry shift
        combined = cv2.addWeighted(diff_col_mag, 0.6, edge_diff, 0.4, 0)
        return combined

    elif diff_mode == "Structural Edge Difference":
        g_before = to_grayscale(before_img)
        g_after = to_grayscale(after_img)
        if k > 1:
            g_before = cv2.GaussianBlur(g_before, (k, k), 0)
            g_after = cv2.GaussianBlur(g_after, (k, k), 0)

        diff_gray = cv2.absdiff(g_before, g_after)
        lap_b = cv2.Laplacian(g_before, cv2.CV_16S, ksize=3)
        lap_a = cv2.Laplacian(g_after, cv2.CV_16S, ksize=3)
        diff_edge = cv2.absdiff(lap_b, lap_a)
        diff_edge = cv2.convertScaleAbs(diff_edge)

        return cv2.addWeighted(diff_gray, 0.6, diff_edge, 0.4, 0)

    elif diff_mode == "Grayscale Difference":
        g_before = to_grayscale(before_img)
        g_after = to_grayscale(after_img)
        if k > 1:
            g_before = cv2.GaussianBlur(g_before, (k, k), 0)
            g_after = cv2.GaussianBlur(g_after, (k, k), 0)
        return cv2.absdiff(g_before, g_after)

    else:
        # Default: Color-Aware Absolute Difference
        if k > 1:
            b_blur = cv2.GaussianBlur(before_img, (k, k), 0)
            a_blur = cv2.GaussianBlur(after_img, (k, k), 0)
        else:
            b_blur = before_img
            a_blur = after_img

        diff_channels = cv2.absdiff(b_blur, a_blur)
        if len(diff_channels.shape) == 3:
            return np.mean(diff_channels, axis=2).astype(np.uint8)
        return diff_channels


def threshold_difference(
    diff_map: np.ndarray,
    threshold_type: str = "Otsu Automatic",
    manual_threshold: int = 35
) -> Tuple[np.ndarray, int]:
    """
    Convert difference map to binary mask (255 = Changed, 0 = Unchanged).
    Returns (binary_mask, computed_threshold_value).
    """
    if threshold_type == "Otsu Automatic":
        thresh_val, mask = cv2.threshold(diff_map, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return mask, int(thresh_val)
    elif threshold_type == "Adaptive Gaussian":
        mask = cv2.adaptiveThreshold(
            diff_map, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 21, -2
        )
        return mask, manual_threshold
    else:
        # Manual threshold
        _, mask = cv2.threshold(diff_map, manual_threshold, 255, cv2.THRESH_BINARY)
        return mask, manual_threshold


def apply_morphological_cleanup(
    mask: np.ndarray,
    kernel_size: int = 3,
    min_contour_area: int = 40
) -> np.ndarray:
    """
    Clean binary mask using morphological opening and closing,
    and eliminate small noise speckles below min_contour_area.
    """
    if kernel_size > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
    else:
        cleaned = mask.copy()

    if min_contour_area > 0:
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_mask = np.zeros_like(cleaned)
        for cnt in contours:
            if cv2.contourArea(cnt) >= min_contour_area:
                cv2.drawContours(filtered_mask, [cnt], -1, 255, thickness=-1)
        return filtered_mask

    return cleaned


def extract_change_metrics(
    mask: np.ndarray,
    min_area: int = 40
) -> Dict[str, Any]:
    """
    Calculate summary metrics from the binary change mask.
    """
    total_pixels = mask.size
    changed_pixels = int(np.count_nonzero(mask))
    change_percentage = (changed_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    significant_contours = [c for c in contours if cv2.contourArea(c) >= min_area]

    bounding_boxes = []
    total_area_sum = 0
    for cnt in significant_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        total_area_sum += area
        bounding_boxes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h), "area": float(area)})

    return {
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "change_percentage": change_percentage,
        "region_count": len(significant_contours),
        "bounding_boxes": bounding_boxes,
        "mean_region_size": (total_area_sum / len(significant_contours)) if significant_contours else 0.0
    }


def generate_change_overlay(
    base_image: np.ndarray,
    mask: np.ndarray,
    overlay_color: Tuple[int, int, int] = (255, 30, 30),
    alpha: float = 0.45,
    draw_bounding_boxes: bool = True,
    draw_contours: bool = True,
    box_color: Tuple[int, int, int] = (0, 240, 255),
    min_box_area: int = 60
) -> np.ndarray:
    """
    Create a professional geospatial overlay with colored alpha highlighting,
    contour outlines, and optional bounding boxes with region numbering.
    """
    overlay = base_image.copy()
    h, w = base_image.shape[:2]

    if mask.shape[:2] != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

    # Highlight changed pixels with semi-transparent overlay
    change_indices = mask > 0
    if np.any(change_indices):
        colored_layer = base_image.copy()
        colored_layer[change_indices] = overlay_color
        overlay = cv2.addWeighted(colored_layer, alpha, overlay, 1.0 - alpha, 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if draw_contours and contours:
        cv2.drawContours(overlay, contours, -1, (255, 50, 50), 2)

    if draw_bounding_boxes and contours:
        box_idx = 1
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= min_box_area:
                x, y, bw, bh = cv2.boundingRect(cnt)
                cv2.rectangle(overlay, (x, y), (x + bw, y + bh), box_color, 2)
                label = f"#{box_idx}"
                cv2.putText(
                    overlay, label, (x, max(15, y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_color, 1, cv2.LINE_AA
                )
                box_idx += 1

    return overlay


def generate_diff_heatmap(diff_map: np.ndarray) -> np.ndarray:
    """Generate a vibrant color heatmap (Inferno style) from the difference map."""
    norm_diff = cv2.normalize(diff_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    heatmap_bgr = cv2.applyColorMap(norm_diff, cv2.COLORMAP_INFERNO)
    return cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)


def draw_tile_grid_overlay(
    image: np.ndarray,
    tile_info_list: List[Dict[str, Any]],
    line_color: Tuple[int, int, int] = (0, 255, 200),
    text_color: Tuple[int, int, int] = (255, 255, 255)
) -> np.ndarray:
    """
    Draw tile partitioning grid lines and tile identifiers over the satellite image.
    """
    vis = image.copy()
    for tile in tile_info_list:
        y1, y2, x1, x2 = tile["bbox"]
        tid = tile["tile_id"]
        cnt = tile.get("changed_count", 0)

        # Draw tile border
        cv2.rectangle(vis, (x1, y1), (x2, y2), line_color, 1)

        # Draw tile label badge
        label = f"Tile #{tid}"
        badge_w, badge_h = 75, 20
        cv2.rectangle(vis, (x1 + 4, y1 + 4), (x1 + 4 + badge_w, y1 + 4 + badge_h), (20, 30, 45), -1)
        cv2.putText(vis, label, (x1 + 8, y1 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.38, text_color, 1, cv2.LINE_AA)

    return vis


def execute_tile_pipeline(
    tile_before: np.ndarray,
    tile_after: np.ndarray,
    diff_mode: str,
    blur_kernel: int,
    threshold_type: str,
    manual_threshold: int,
    morph_kernel: int,
    min_area: int
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Self-contained tile processing routine executed by worker processes.
    """
    diff_tile = compute_difference_map(
        tile_before, tile_after, diff_mode=diff_mode, blur_kernel=blur_kernel
    )

    mask_tile, _ = threshold_difference(
        diff_tile, threshold_type=threshold_type, manual_threshold=manual_threshold
    )

    clean_tile = apply_morphological_cleanup(
        mask_tile, kernel_size=morph_kernel, min_contour_area=min_area
    )

    changed_count = int(np.count_nonzero(clean_tile))
    return diff_tile, clean_tile, changed_count
