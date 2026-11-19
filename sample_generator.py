"""
sample_generator.py
===================
Generates high-resolution, visually realistic synthetic satellite image pairs (Before / After)
simulating real-world geospatial change events:
1. Urban Development (New warehouses, residential grids, commercial buildings)
2. Deforestation (Clear-cutting in rainforest, logging tracks, bare soil)
3. Highway & Infrastructure (New multi-lane highway, cloverleaf interchange, overpasses)
4. Reservoir Water Level Dynamics (Reservoir shoreline retreat, exposed sediment)
"""

import os
import cv2
import numpy as np
from PIL import Image

def generate_perlin_noise_2d(shape, res):
    """Generate smooth continuous fractal/gradient noise for terrain textures."""
    def f(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1

    # Gradients
    np.random.seed(42)
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)

    # Pad or slice to exact shape
    def fit_shape(arr, target_shape):
        h, w = arr.shape[:2]
        th, tw = target_shape[:2]
        if h < th or w < tw:
            arr = cv2.resize(arr, (tw, th))
        return arr[:th, :tw]

    g00 = fit_shape(g00, shape)
    g10 = fit_shape(g10, shape)
    g01 = fit_shape(g01, shape)
    g11 = fit_shape(g11, shape)
    grid = fit_shape(grid, shape)

    n00 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)

    t = f(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    noise = (np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1))
    # Normalize to 0-1
    return (noise - noise.min()) / (noise.max() - noise.min() + 1e-6)


def create_terrain_base(h, w, terrain_type="rural_green"):
    """Create realistic satellite base layer with natural vegetation, soil, and river."""
    noise1 = generate_perlin_noise_2d((h, w), (8, 8))
    noise2 = generate_perlin_noise_2d((h, w), (16, 16))
    fine_noise = generate_perlin_noise_2d((h, w), (32, 32))
    composite_noise = 0.55 * noise1 + 0.3 * noise2 + 0.15 * fine_noise

    base = np.zeros((h, w, 3), dtype=np.uint8)

    if terrain_type == "rural_green":
        # Green canopy, fields, and agricultural patterns
        for y in range(h):
            for x in range(0, w, 80):
                pass
        # Color mapping: dark green to olive and pale brown soil
        c_dark_green = np.array([38, 70, 35], dtype=np.float32)
        c_light_green = np.array([72, 115, 60], dtype=np.float32)
        c_soil = np.array([130, 110, 80], dtype=np.float32)

        t_factor = composite_noise[:, :, np.newaxis]
        rgb = np.where(t_factor < 0.6,
                       c_dark_green + (c_light_green - c_dark_green) * (t_factor / 0.6),
                       c_light_green + (c_soil - c_light_green) * ((t_factor - 0.6) / 0.4))
        base = np.clip(rgb, 0, 255).astype(np.uint8)

        # Add natural winding river
        curve_pts = []
        for x in range(0, w, 40):
            y = int(h * 0.35 + np.sin(x * 0.005) * 80 + np.cos(x * 0.015) * 35)
            curve_pts.append([x, y])
        curve_pts = np.array(curve_pts, dtype=np.int32)
        cv2.polylines(base, [curve_pts], isClosed=False, color=(35, 75, 110), thickness=28)

    elif terrain_type == "tropical_rainforest":
        c_canopy1 = np.array([20, 55, 25], dtype=np.float32)
        c_canopy2 = np.array([35, 85, 40], dtype=np.float32)
        c_clearing = np.array([90, 75, 50], dtype=np.float32)

        t_factor = composite_noise[:, :, np.newaxis]
        rgb = np.where(t_factor < 0.8,
                       c_canopy1 + (c_canopy2 - c_canopy1) * (t_factor / 0.8),
                       c_canopy2 + (c_clearing - c_canopy2) * ((t_factor - 0.8) / 0.2))
        base = np.clip(rgb, 0, 255).astype(np.uint8)

        # Winding jungle river
        curve_pts = []
        for y in range(0, h, 30):
            x = int(w * 0.5 + np.sin(y * 0.004) * 120 + np.cos(y * 0.01) * 45)
            curve_pts.append([x, y])
        curve_pts = np.array(curve_pts, dtype=np.int32)
        cv2.polylines(base, [curve_pts], isClosed=False, color=(28, 62, 85), thickness=36)

    elif terrain_type == "semi_arid":
        c_sand = np.array([175, 155, 125], dtype=np.float32)
        c_rock = np.array([135, 115, 95], dtype=np.float32)
        c_scrub = np.array([95, 105, 75], dtype=np.float32)

        t_factor = composite_noise[:, :, np.newaxis]
        rgb = np.where(t_factor < 0.5,
                       c_sand + (c_rock - c_sand) * (t_factor / 0.5),
                       c_rock + (c_scrub - c_rock) * ((t_factor - 0.5) / 0.5))
        base = np.clip(rgb, 0, 255).astype(np.uint8)

    # Add realistic satellite atmospheric grain
    grain = np.random.normal(0, 3.5, base.shape).astype(np.int16)
    base = np.clip(base.astype(np.int16) + grain, 0, 255).astype(np.uint8)
    return base


def generate_urban_development_dataset(h=1600, w=1600):
    """Scenario 1: Urban Development & Industrial Warehouses."""
    before = create_terrain_base(h, w, "rural_green")

    # Add narrow old rural road
    cv2.line(before, (0, int(h * 0.7)), (w, int(h * 0.65)), (110, 100, 85), 8)

    # Some old small rural houses
    for (rx, ry) in [(200, 300), (350, 420), (500, 260)]:
        cv2.rectangle(before, (rx, ry), (rx + 40, ry + 35), (145, 135, 120), -1)
        # Shadow
        cv2.rectangle(before, (rx + 40, ry), (rx + 48, ry + 35), (25, 45, 25), -1)

    after = before.copy()

    # 1. New Major Dual-Lane Arterial Highway
    cv2.line(after, (0, int(h * 0.7)), (w, int(h * 0.65)), (55, 55, 58), 24)
    # Highway white center line markings
    cv2.line(after, (0, int(h * 0.7)), (w, int(h * 0.65)), (220, 220, 225), 2)

    # 2. Huge Industrial Logistics Complex
    # Warehouse 1
    w1_x, w1_y, w1_w, w1_h = 250, 750, 320, 180
    cv2.rectangle(after, (w1_x - 30, w1_y - 20), (w1_x + w1_w + 30, w1_y + w1_h + 40), (85, 88, 92), -1) # Asphalt apron
    cv2.rectangle(after, (w1_x, w1_y), (w1_x + w1_w, w1_y + w1_h), (210, 215, 225), -1) # Metal Roof
    cv2.rectangle(after, (w1_x + w1_w, w1_y), (w1_x + w1_w + 18, w1_y + w1_h), (30, 35, 40), -1) # Shadow
    # Roof vents/HVAC units
    for vx in range(w1_x + 30, w1_x + w1_w - 20, 45):
        cv2.rectangle(after, (vx, w1_y + 40), (vx + 18, w1_y + 60), (140, 145, 155), -1)
        cv2.rectangle(after, (vx, w1_y + 110), (vx + 18, w1_y + 130), (140, 145, 155), -1)

    # Warehouse 2
    w2_x, w2_y, w2_w, w2_h = 680, 720, 380, 220
    cv2.rectangle(after, (w2_x - 25, w2_y - 20), (w2_x + w2_w + 25, w2_y + w2_h + 35), (80, 82, 86), -1)
    cv2.rectangle(after, (w2_x, w2_y), (w2_x + w2_w, w2_y + w2_h), (195, 200, 210), -1)
    cv2.rectangle(after, (w2_x + w2_w, w2_y), (w2_x + w2_w + 20, w2_y + w2_h), (30, 35, 40), -1)

    # 3. New Residential Subdivisions (top right)
    grid_start_x, grid_start_y = 1050, 150
    # Neighborhood access streets
    for off_y in range(0, 450, 100):
        cv2.line(after, (grid_start_x - 30, grid_start_y + off_y), (grid_start_x + 450, grid_start_y + off_y), (70, 72, 75), 10)
    for off_x in range(0, 450, 110):
        cv2.line(after, (grid_start_x + off_x, grid_start_y - 30), (grid_start_x + off_x, grid_start_y + 430), (70, 72, 75), 10)

    # Suburban houses with terracotta and blue roofs
    for off_y in range(25, 400, 100):
        for off_x in range(25, 400, 110):
            roof_col = (185, 80, 60) if (off_x + off_y) % 2 == 0 else (75, 110, 145)
            cv2.rectangle(after, (grid_start_x + off_x, grid_start_y + off_y),
                          (grid_start_x + off_x + 55, grid_start_y + off_y + 45), roof_col, -1)
            # shadow
            cv2.rectangle(after, (grid_start_x + off_x + 55, grid_start_y + off_y),
                          (grid_start_x + off_x + 63, grid_start_y + off_y + 45), (35, 40, 45), -1)

    # 4. Construction site with excavators and cleared soil (bottom right)
    cv2.rectangle(after, (1150, 1050), (1480, 1400), (160, 130, 95), -1)
    # Foundation trenches
    for ty in range(1100, 1350, 60):
        cv2.rectangle(after, (1190, ty), (1420, ty + 25), (75, 60, 45), -1)

    return before, after


def generate_deforestation_dataset(h=1600, w=1600):
    """Scenario 2: Tropical Rainforest Deforestation & Clear-Cutting."""
    before = create_terrain_base(h, w, "tropical_rainforest")
    after = before.copy()

    # 1. Major clear-cut zone 1 (top left quadrant)
    pts1 = np.array([
        [150, 180], [580, 120], [620, 480], [450, 590], [180, 520]
    ], np.int32)
    cv2.fillPoly(after, [pts1], (148, 112, 78)) # Bare brown soil
    # Add burnt patches / charred logs
    for cy in range(220, 460, 70):
        cv2.ellipse(after, (360, cy), (60, 25), 15, 0, 360, (75, 55, 40), -1)

    # 2. Major clear-cut zone 2 (bottom center)
    pts2 = np.array([
        [650, 950], [1150, 920], [1220, 1380], [600, 1420]
    ], np.int32)
    cv2.fillPoly(after, [pts2], (165, 128, 85))
    # Agricultural furrow patterns
    for fy in range(970, 1370, 30):
        cv2.line(after, (670, fy), (1180, fy - 15), (135, 100, 65), 3)

    # 3. Illegal logging branch corridors (fishbone roads cutting into forest)
    spine_x = 900
    cv2.line(after, (spine_x, 100), (spine_x, 850), (155, 120, 85), 12)
    for off_y in range(180, 800, 90):
        # Left spur
        cv2.line(after, (spine_x, off_y), (spine_x - 180, off_y + 40), (145, 110, 75), 8)
        # Right spur
        cv2.line(after, (spine_x, off_y + 35), (spine_x + 220, off_y + 70), (145, 110, 75), 8)

    return before, after


def generate_infrastructure_dataset(h=1600, w=1600):
    """Scenario 3: New Multi-Lane Highway & Interchange System."""
    before = create_terrain_base(h, w, "semi_arid")

    # Modest 2-lane country road
    cv2.line(before, (0, int(h * 0.45)), (w, int(h * 0.55)), (115, 105, 95), 10)
    after = before.copy()

    # 1. Massive 6-Lane Concrete Expressway running diagonally
    cv2.line(after, (0, 250), (w, 1350), (60, 62, 65), 44)
    # Median barrier
    cv2.line(after, (0, 250), (w, 1350), (160, 165, 170), 4)
    # Lane stripes
    cv2.line(after, (0, 235), (w, 1335), (230, 230, 230), 2)
    cv2.line(after, (0, 265), (w, 1365), (230, 230, 230), 2)

    # 2. Modern Cloverleaf Interchange at the intersection
    center_x, center_y = int(w * 0.5), int(h * 0.5)
    # Ramps
    for dx, dy, angle_start, angle_end in [
        (-120, -120, 0, 90),
        (120, -120, 90, 180),
        (120, 120, 180, 270),
        (-120, 120, 270, 360)
    ]:
        cv2.ellipse(after, (center_x + dx, center_y + dy), (160, 160), 0, angle_start, angle_end, (70, 72, 75), 16)
        cv2.ellipse(after, (center_x + dx, center_y + dy), (160, 160), 0, angle_start, angle_end, (220, 220, 220), 2)

    # 3. New Commercial Logistics Park near junction
    p_x, p_y = 950, 200
    cv2.rectangle(after, (p_x - 20, p_y - 20), (p_x + 380, p_y + 260), (75, 75, 78), -1)
    cv2.rectangle(after, (p_x, p_y), (p_x + 340, p_y + 220), (210, 215, 225), -1)
    cv2.rectangle(after, (p_x + 340, p_y), (p_x + 355, p_y + 220), (35, 40, 45), -1)

    return before, after


def generate_reservoir_drought_dataset(h=1600, w=1600):
    """Scenario 4: Reservoir Shoreline Retreat & Drought Impact."""
    before = create_terrain_base(h, w, "rural_green")

    # Before: Big full reservoir
    water_pts = np.array([
        [150, 150], [900, 200], [1400, 600], [1300, 1250], [700, 1400], [250, 1100], [100, 650]
    ], np.int32)
    cv2.fillPoly(before, [water_pts], (35, 80, 120)) # Deep reservoir blue
    # Green lush littoral buffer
    cv2.polylines(before, [water_pts], True, (50, 115, 65), 35)

    after = before.copy()

    # After: Severe drought - water retreated drastically
    shrunk_pts = np.array([
        [400, 380], [800, 420], [1100, 750], [1000, 1050], [650, 1150], [420, 920], [350, 620]
    ], np.int32)

    # The area between old shoreline and new shoreline turns into dry exposed lakebed silt
    cv2.fillPoly(after, [water_pts], (185, 165, 135)) # Exposed pale sediment
    # Cracked mud flat lines
    for ly in range(250, 1200, 40):
        cv2.line(after, (200, ly), (1200, ly + 15), (150, 130, 105), 2)
    # Remaining shrunken water
    cv2.fillPoly(after, [shrunk_pts], (25, 65, 95))

    return before, after


def generate_all_samples(target_dir):
    """Generate and save all 4 sample datasets to target_dir as high-res PNGs."""
    os.makedirs(target_dir, exist_ok=True)
    datasets = [
        ("urban_development", generate_urban_development_dataset, "Urban Expansion & Industrial Construction"),
        ("deforestation", generate_deforestation_dataset, "Tropical Rainforest Deforestation & Roads"),
        ("infrastructure", generate_infrastructure_dataset, "Highway & Interchange Infrastructure"),
        ("reservoir_drought", generate_reservoir_drought_dataset, "Reservoir Retreat & Drought Dynamics")
    ]

    for name, gen_func, desc in datasets:
        b_path = os.path.join(target_dir, f"{name}_before.png")
        a_path = os.path.join(target_dir, f"{name}_after.png")

        print(f"Generating dataset: {name} ({desc})...")
        b_img, a_img = gen_func(1600, 1600)

        Image.fromarray(b_img).save(b_path, format="PNG", optimize=True)
        Image.fromarray(a_img).save(a_path, format="PNG", optimize=True)
        print(f"Saved: {b_path} and {a_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Asus\.gemini\antigravity\scratch\parallel-satellite-change-detection\samples"
    generate_all_samples(out_dir)
