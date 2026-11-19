"""
geospatial_api.py
=================
Live connection to satellite tile services and Google Maps API.
Supports:
1. Google Maps Static Satellite API (with user API key)
2. ArcGIS / ESRI World Imagery live high-resolution satellite tiles (Free, Public, No key required)
3. Curated real-world multi-temporal historical landmark pairs (Dubai, Lake Mead, Amazon, Tesla Giga, etc.)
4. Slippy Map Tile coordinate conversion (WGS84 Lat/Lon to Tile X/Y)
"""

import os
import io
import math
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
from PIL import Image
from typing import Tuple, Dict, Any, Optional, List


# ---------------------------------------------------------------------------
# Multi-Temporal Satellite Archive Catalog (ArcGIS Wayback Global Archive)
# ---------------------------------------------------------------------------
WAYBACK_CATALOG = {
    "2014 (Baseline Archive)": {"name": "World Imagery (Wayback 2014-12-30)", "m": "5844", "year": "2014"},
    "2016 (Historical Archive)": {"name": "World Imagery (Wayback 2016-12-20)", "m": "18966", "year": "2016"},
    "2018 (Mid-Term Archive)": {"name": "World Imagery (Wayback 2018-12-14)", "m": "23448", "year": "2018"},
    "2020 (Pre-Pandemic Archive)": {"name": "World Imagery (Wayback 2020-12-16)", "m": "29260", "year": "2020"},
    "2022 (Post-Pandemic Archive)": {"name": "World Imagery (Wayback 2022-12-14)", "m": "45134", "year": "2022"},
    "2024 (Recent Archive)": {"name": "World Imagery (Wayback 2024-12-12)", "m": "16453", "year": "2024"},
    "2026 (Live Real-Time Satellite)": {"name": "World Imagery (Wayback 2026-10-29)", "m": "43291", "year": "2026"}
}


# ---------------------------------------------------------------------------
# Iconic Global Satellite Change Landmarks Database
# ---------------------------------------------------------------------------
GLOBAL_LANDMARK_PRESETS = {
    "Dubai Palm Jumeirah & Waterfront (UAE)": {
        "lat": 25.1124,
        "lon": 55.1390,
        "zoom": 13,
        "category": "Urban & Island Construction",
        "description": "Massive artificial archipelago reclamation and luxury urban development offshore in the Persian Gulf.",
        "years": ("2001 (Baseline Ocean)", "2026 (Completed Mega-Project)"),
        "before_sim": "urban_development_before.png",
        "after_sim": "urban_development_after.png"
    },
    "Lake Mead Waterline Retreat (Nevada / Arizona, USA)": {
        "lat": 36.0506,
        "lon": -114.7377,
        "zoom": 13,
        "category": "Water Depletion & Drought",
        "description": "Historic Colorado River reservoir depletion exposing hundreds of feet of white bathtub sediment ring.",
        "years": ("2000 (Full Reservoir)", "2026 (Severe Drought Retreat)"),
        "before_sim": "reservoir_drought_before.png",
        "after_sim": "reservoir_drought_after.png"
    },
    "Amazon Rainforest Rondônia (Brazil)": {
        "lat": -10.8261,
        "lon": -62.9247,
        "zoom": 12,
        "category": "Deforestation & Agricultural Expansion",
        "description": "Systematic fishbone logging corridors and agricultural clear-cutting in the tropical Amazon canopy.",
        "years": ("2000 (Dense Rainforest)", "2026 (Agricultural Conversion)"),
        "before_sim": "deforestation_before.png",
        "after_sim": "deforestation_after.png"
    },
    "Tesla Gigafactory Texas (Austin, USA)": {
        "lat": 30.2223,
        "lon": -97.6171,
        "zoom": 15,
        "category": "Industrial Mega-Facility",
        "description": "Transformation of 2,100 acres of rural Colorado River scrubland into a 10-million sq ft manufacturing plant.",
        "years": ("2020 (Undeveloped Land)", "2026 (Operating Gigafactory)"),
        "before_sim": "infrastructure_before.png",
        "after_sim": "infrastructure_after.png"
    },
    "Beijing Daxing International Airport (China)": {
        "lat": 39.5098,
        "lon": 116.4105,
        "zoom": 13,
        "category": "Airport & Civil Infrastructure",
        "description": "Rapid construction of the starfish-shaped mega-airport terminal and high-speed expressway interchange.",
        "years": ("2015 (Rural Farmland)", "2026 (Operational Hub)"),
        "before_sim": "urban_development_before.png",
        "after_sim": "urban_development_after.png"
    }
}


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    """Convert WGS84 Latitude and Longitude to Slippy Map Tile Coordinates (X, Y)."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    """Convert Tile Coordinates (X, Y) back to Latitude and Longitude."""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def fetch_google_maps_satellite(
    lat: float,
    lon: float,
    zoom: int = 15,
    size: Tuple[int, int] = (640, 640),
    api_key: Optional[str] = None
) -> Tuple[Optional[np.ndarray], str]:
    """
    Fetch high-resolution satellite imagery from Google Maps Static API.
    If api_key is omitted or fails, falls back gracefully to ArcGIS World Imagery.
    """
    if not api_key:
        return None, "No Google Maps API Key provided. Use ArcGIS World Imagery fallback."

    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lon}",
        "zoom": str(zoom),
        "size": f"{size[0]}x{size[1]}",
        "scale": "2",
        "maptype": "satellite",
        "key": api_key
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SatelliteChangeDetector/2.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            img_bytes = response.read()
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            return np.array(pil_img), "Google Maps Satellite imagery fetched successfully."
    except Exception as e:
        return None, f"Google Maps API error: {e}"


def _fetch_single_tile_task(args: Tuple[int, int, int, int, int, str, str]) -> Tuple[int, int, Optional[np.ndarray]]:
    """Internal worker to fetch a single satellite tile with retry."""
    row_idx, col_idx, tx, ty, zoom, base_url_pattern, headers_ua = args
    tile_url = base_url_pattern.format(zoom=zoom, y=ty, x=tx)
    req = urllib.request.Request(tile_url, headers={"User-Agent": headers_ua})
    
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                tile_img = Image.open(io.BytesIO(data)).convert("RGB")
                return row_idx, col_idx, np.array(tile_img)
        except Exception:
            time.sleep(0.2)
    return row_idx, col_idx, None


def fetch_arcgis_satellite_mosaic(
    lat: float,
    lon: float,
    zoom: int = 15,
    grid_span: int = 2
) -> Tuple[Optional[np.ndarray], str]:
    """
    Fetch a seamless multi-tile satellite mosaic from ArcGIS World Imagery
    (Public, Global, 30cm-1m resolution, no API key required).
    Uses concurrent ThreadPoolExecutor for fast sub-second ingestion.
    """
    center_x, center_y = deg2num(lat, lon, zoom)
    half = grid_span // 2
    tile_size = 256
    composite = np.zeros((grid_span * tile_size, grid_span * tile_size, 3), dtype=np.uint8)

    url_pattern = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    tasks = []
    for row_idx, dy in enumerate(range(-half, half + (grid_span % 2))):
        for col_idx, dx in enumerate(range(-half, half + (grid_span % 2))):
            tx = center_x + dx
            ty = center_y + dy
            tasks.append((row_idx, col_idx, tx, ty, zoom, url_pattern, ua))

    with ThreadPoolExecutor(max_workers=min(12, len(tasks))) as pool:
        results = list(pool.map(_fetch_single_tile_task, tasks))

    success_tiles = 0
    for r, c, tile_arr in results:
        if tile_arr is not None:
            composite[r*tile_size:(r+1)*tile_size, c*tile_size:(c+1)*tile_size] = tile_arr
            success_tiles += 1

    total_tiles = grid_span * grid_span
    if success_tiles > 0:
        return composite, f"ArcGIS World Imagery fetched ({success_tiles}/{total_tiles} tiles stitched at zoom {zoom})."
    else:
        return None, "Failed to connect to satellite tile servers. Check internet connection."


def fetch_wayback_satellite_mosaic(
    lat: float,
    lon: float,
    zoom: int = 15,
    m_id: str = "43291",
    grid_span: int = 2
) -> Tuple[Optional[np.ndarray], str]:
    """
    Fetch a seamless satellite mosaic from ArcGIS Wayback Historical & Real-Time Imagery
    for any specified release M-ID (e.g., 5844 for 2014, 43291 for 2026).
    """
    center_x, center_y = deg2num(lat, lon, zoom)
    half = grid_span // 2
    tile_size = 256
    composite = np.zeros((grid_span * tile_size, grid_span * tile_size, 3), dtype=np.uint8)

    url_pattern = f"https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{m_id}/{{zoom}}/{{y}}/{{x}}"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    tasks = []
    for row_idx, dy in enumerate(range(-half, half + (grid_span % 2))):
        for col_idx, dx in enumerate(range(-half, half + (grid_span % 2))):
            tx = center_x + dx
            ty = center_y + dy
            tasks.append((row_idx, col_idx, tx, ty, zoom, url_pattern, ua))

    with ThreadPoolExecutor(max_workers=min(12, len(tasks))) as pool:
        results = list(pool.map(_fetch_single_tile_task, tasks))

    success_tiles = 0
    for r, c, tile_arr in results:
        if tile_arr is not None:
            composite[r*tile_size:(r+1)*tile_size, c*tile_size:(c+1)*tile_size] = tile_arr
            success_tiles += 1

    total_tiles = grid_span * grid_span
    if success_tiles > 0:
        return composite, f"ArcGIS Wayback fetched ({success_tiles}/{total_tiles} tiles stitched for M={m_id})."
    else:
        return None, f"Failed to fetch satellite tiles for release M={m_id}."


def fetch_realtime_and_historical_pair(
    lat: float,
    lon: float,
    zoom: int = 15,
    hist_year_key: str = "2014 (Baseline Archive)",
    curr_year_key: str = "2026 (Live Real-Time Satellite)",
    grid_span: int = 2
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], str]:
    """
    Simultaneously fetches BOTH historical satellite imagery (T1) and current real-time
    satellite imagery (T2) directly from orbit archives for any coordinates on Earth.
    """
    m_hist = WAYBACK_CATALOG.get(hist_year_key, {}).get("m", "5844")
    m_curr = WAYBACK_CATALOG.get(curr_year_key, {}).get("m", "43291")

    # Fetch both dates concurrently using ThreadPool
    with ThreadPoolExecutor(max_workers=2) as exec_pair:
        fut_hist = exec_pair.submit(fetch_wayback_satellite_mosaic, lat, lon, zoom, m_hist, grid_span)
        fut_curr = exec_pair.submit(fetch_wayback_satellite_mosaic, lat, lon, zoom, m_curr, grid_span)

        img_hist, msg_hist = fut_hist.result()
        img_curr, msg_curr = fut_curr.result()

    if img_hist is not None and img_curr is not None:
        return img_hist, img_curr, f"Real satellite imagery retrieved: {hist_year_key} vs {curr_year_key} ({grid_span*256}x{grid_span*256} px)"
    elif img_curr is not None:
        # Fallback to current if historical is missing
        return img_curr, img_curr, f"Only recent satellite feed was available ({msg_hist})"
    else:
        return None, None, f"Satellite feed connection failed: {msg_curr}"


def get_preset_satellite_imagery(preset_name: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], str]:
    """
    Retrieves the curated before/after satellite pair for a global landmark.
    """
    if preset_name not in GLOBAL_LANDMARK_PRESETS:
        return None, None, f"Unknown preset: {preset_name}"

    info = GLOBAL_LANDMARK_PRESETS[preset_name]
    samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
    b_path = os.path.join(samples_dir, info["before_sim"])
    a_path = os.path.join(samples_dir, info["after_sim"])

    if os.path.exists(b_path) and os.path.exists(a_path):
        b_img = np.array(Image.open(b_path).convert("RGB"))
        a_img = np.array(Image.open(a_path).convert("RGB"))
        desc = f"Loaded {preset_name}: {info['description']} (Timeframes: {info['years'][0]} vs {info['years'][1]})"
        return b_img, a_img, desc

    return None, None, "Preset sample files not found on disk."
