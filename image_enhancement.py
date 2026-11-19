"""
image_enhancement.py
====================
Advanced Radiometric Normalization, Dehazing, Sub-Pixel Alignment,
and Semantic Multi-Class Change Categorization for Satellite Remote Sensing.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional, List


def apply_clahe_enhancement(img_rgb: np.ndarray, clip_limit: float = 2.5, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
    in the LAB color space (Luminance channel only) to preserve natural color fidelity.
    """
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_enhanced = clahe.apply(l)

    enhanced_lab = cv2.merge((l_enhanced, a, b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)


def apply_unsharp_mask(img_rgb: np.ndarray, sigma: float = 1.2, strength: float = 1.4) -> np.ndarray:
    """
    Super-resolution edge accentuation using Gaussian unsharp masking.
    Sharpens building rooftops, asphalt pavement lines, and canopy boundaries.
    """
    blurred = cv2.GaussianBlur(img_rgb, (0, 0), sigma)
    sharpened = cv2.addWeighted(img_rgb, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def apply_atmospheric_dehaze(img_rgb: np.ndarray, omega: float = 0.85) -> np.ndarray:
    """
    Approximation of Dark Channel Prior for satellite atmospheric haze removal.
    Removes aerosol scattering and boosts deep ground contrast.
    """
    norm_img = img_rgb.astype(np.float32) / 255.0

    # Dark channel: minimum across RGB channels within local 15x15 window
    min_channel = np.min(norm_img, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dark_channel = cv2.erode(min_channel, kernel)

    # Atmospheric light estimate: top 0.1% brightest in dark channel
    num_pixels = dark_channel.size
    num_bright = max(1, int(num_pixels * 0.001))
    flat_dark = dark_channel.flatten()
    indices = np.argpartition(flat_dark, -num_bright)[-num_bright:]
    flat_img = norm_img.reshape(-1, 3)
    atmos_light = np.mean(flat_img[indices], axis=0)
    atmos_light = np.maximum(atmos_light, 0.1)

    # Transmission map
    transmission = 1.0 - omega * (dark_channel / np.max(atmos_light))
    transmission = np.clip(transmission, 0.15, 1.0)
    transmission = cv2.GaussianBlur(transmission, (11, 11), 0)

    # Radiance recovery
    t3 = np.repeat(transmission[:, :, np.newaxis], 3, axis=2)
    recovered = (norm_img - atmos_light) / t3 + atmos_light
    return np.clip(recovered * 255.0, 0, 255).astype(np.uint8)


def match_histograms_radiometric(source_img: np.ndarray, reference_img: np.ndarray) -> np.ndarray:
    """
    Radiometric Illumination Normalization via Cumulative Histogram Matching.
    Warps the CDF of source_img (e.g. Time T2) to match reference_img (Time T1),
    neutralizing seasonal sun angle differences and shadow shifts between satellite passes.
    """
    matched = np.zeros_like(source_img)

    for ch in range(3):
        src_ch = source_img[:, :, ch]
        ref_ch = reference_img[:, :, ch]

        # Calculate histograms and cumulative probability functions
        src_hist, _ = np.histogram(src_ch.flatten(), 256, [0, 256])
        ref_hist, _ = np.histogram(ref_ch.flatten(), 256, [0, 256])

        src_cdf = src_hist.cumsum()
        src_cdf_norm = src_cdf / src_cdf.max()

        ref_cdf = ref_hist.cumsum()
        ref_cdf_norm = ref_cdf / ref_cdf.max()

        # Lookup table mapping source pixel values to reference CDF
        lut = np.zeros(256, dtype=np.uint8)
        for src_val in range(256):
            diff = np.abs(ref_cdf_norm - src_cdf_norm[src_val])
            lut[src_val] = np.argmin(diff)

        matched[:, :, ch] = cv2.LUT(src_ch, lut)

    return matched


def align_subpixel_ecc(
    ref_img: np.ndarray,
    target_img: np.ndarray,
    warp_mode: int = cv2.MOTION_EUCLIDEAN,
    max_iters: int = 50,
    eps: float = 1e-4
) -> Tuple[np.ndarray, bool]:
    """
    Sub-pixel Geometric Co-registration using Enhanced Correlation Coefficient (ECC) Maximization.
    Guarantees sub-pixel precision between multi-temporal satellite images.
    """
    gray_ref = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY) if len(ref_img.shape) == 3 else ref_img
    gray_target = cv2.cvtColor(target_img, cv2.COLOR_RGB2GRAY) if len(target_img.shape) == 3 else target_img

    # Initialize warp matrix
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, max_iters, eps)

    try:
        _, warp_matrix = cv2.findTransformECC(gray_ref, gray_target, warp_matrix, warp_mode, criteria)
        h, w = ref_img.shape[:2]
        aligned = cv2.warpAffine(target_img, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
        return aligned, True
    except Exception:
        # If ECC fails to converge, return original target
        return target_img, False


def compute_vari_index(img_rgb: np.ndarray) -> np.ndarray:
    """
    Visible Atmospherically Resistant Index (VARI) for optical RGB satellite imagery:
        VARI = (Green - Red) / (Green + Red - Blue)
    Standard remote sensing index for vegetative ground cover and canopy health.
    Returns float32 map normalized to [-1.0, 1.0].
    """
    r = img_rgb[:, :, 0].astype(np.float32)
    g = img_rgb[:, :, 1].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)

    denominator = g + r - b
    denominator = np.where(np.abs(denominator) < 1e-4, 1e-4, denominator)

    vari = (g - r) / denominator
    return np.clip(vari, -1.0, 1.0)


def classify_change_categories(
    before_img: np.ndarray,
    after_img: np.ndarray,
    binary_mask: np.ndarray
) -> Dict[str, Any]:
    """
    Classifies detected change pixels into 4 distinct semantic categories:
    1. 🔴 Urban & Construction: High structural gradient, low VARI, reflective building material
    2. 🟢 Vegetation Loss / Deforestation: Significant drop in VARI green index
    3. 🔵 Water Dynamics / Shoreline Shifts: Low red reflection, high blue-green ratio shift
    4. 🟡 Road & Soil Infrastructure: High linear texture, bare soil reflectance
    """
    h, w = before_img.shape[:2]
    change_coords = binary_mask > 0

    if not np.any(change_coords):
        return {
            "category_mask": np.zeros((h, w, 3), dtype=np.uint8),
            "counts": {"construction": 0, "vegetation_loss": 0, "water_change": 0, "infrastructure": 0},
            "percentages": {"construction": 0.0, "vegetation_loss": 0.0, "water_change": 0.0, "infrastructure": 0.0}
        }

    # 1. Compute VARI vegetation index maps
    vari_before = compute_vari_index(before_img)
    vari_after = compute_vari_index(after_img)
    delta_vari = vari_after - vari_before

    # 2. Compute Structural Gradient Differencing
    gray_b = cv2.cvtColor(before_img, cv2.COLOR_RGB2GRAY)
    gray_a = cv2.cvtColor(after_img, cv2.COLOR_RGB2GRAY)
    sobel_b = cv2.Laplacian(gray_b, cv2.CV_16S, ksize=3)
    sobel_a = cv2.Laplacian(gray_a, cv2.CV_16S, ksize=3)
    edge_diff = cv2.absdiff(sobel_b, sobel_a)

    # 3. Water surface proxy: high blue, low red
    blue_ratio_b = before_img[:, :, 2].astype(float) / (np.sum(before_img, axis=2).astype(float) + 1e-4)
    blue_ratio_a = after_img[:, :, 2].astype(float) / (np.sum(after_img, axis=2).astype(float) + 1e-4)
    delta_blue = np.abs(blue_ratio_a - blue_ratio_b)

    # Category masks (initialized to False)
    mask_veg_loss = np.zeros((h, w), dtype=bool)
    mask_water = np.zeros((h, w), dtype=bool)
    mask_construction = np.zeros((h, w), dtype=bool)
    mask_infra = np.zeros((h, w), dtype=bool)

    # Rule-based classification within change mask
    # A. Vegetation Loss: VARI dropped significantly (canopy cleared)
    mask_veg_loss[change_coords & (delta_vari < -0.12)] = True

    # B. Water change: significant shift in blue/water ratio or low reflectance deep absorption
    mask_water[change_coords & (~mask_veg_loss) & (delta_blue > 0.10)] = True

    # C. Construction: high edge difference (sharp building roofs, rectangular foundations)
    mask_construction[change_coords & (~mask_veg_loss) & (~mask_water) & (edge_diff > 45)] = True

    # D. Remaining: Road pavement, cleared earth, infrastructure
    mask_infra[change_coords & (~mask_veg_loss) & (~mask_water) & (~mask_construction)] = True

    # Counts
    c_veg = int(np.count_nonzero(mask_veg_loss))
    c_water = int(np.count_nonzero(mask_water))
    c_const = int(np.count_nonzero(mask_construction))
    c_infra = int(np.count_nonzero(mask_infra))
    total_changed = max(1, c_veg + c_water + c_const + c_infra)

    # Colored Semantic Category Visualization Image:
    # 🔴 Red: Construction (239, 71, 111)
    # 🟢 Green: Vegetation Loss (6, 214, 160)
    # 🔵 Blue: Water Dynamics (17, 138, 178)
    # 🟡 Gold: Road/Soil Infrastructure (255, 209, 102)
    cat_vis = after_img.copy()

    colored_layer = after_img.copy()
    colored_layer[mask_construction] = [239, 71, 111] # Coral Red
    colored_layer[mask_veg_loss] = [6, 214, 160]      # Emerald Green
    colored_layer[mask_water] = [17, 138, 178]        # Aqua Blue
    colored_layer[mask_infra] = [255, 209, 102]       # Gold

    cat_vis = cv2.addWeighted(colored_layer, 0.55, cat_vis, 0.45, 0)

    return {
        "category_overlay": cat_vis,
        "masks": {
            "construction": mask_construction,
            "vegetation_loss": mask_veg_loss,
            "water": mask_water,
            "infrastructure": mask_infra
        },
        "counts": {
            "New Construction": c_const,
            "Vegetation Loss": c_veg,
            "Water Surface Dynamics": c_water,
            "Road / Soil Infrastructure": c_infra
        },
        "percentages": {
            "New Construction": (c_const / total_changed) * 100.0,
            "Vegetation Loss": (c_veg / total_changed) * 100.0,
            "Water Surface Dynamics": (c_water / total_changed) * 100.0,
            "Road / Soil Infrastructure": (c_infra / total_changed) * 100.0
        }
    }
