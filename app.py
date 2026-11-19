"""
app.py
======
SATELLITE CHANGE DETECTION SYSTEM
AI-Assisted Geospatial Analysis Using Parallel Computing

Enhanced with:
- Live Google Maps API & Satellite Tile Connection (ArcGIS World Imagery + Global Landmark Presets)
- Radiometric Normalization, Histogram Matching & Atmospheric Dehazing
- Sub-Pixel Geometric Alignment (ECC Maximization)
- Multi-Class Semantic Change Categorization (New Construction, Vegetation Loss, Water Dynamics, Roads)
- Interactive Draggable Swipe Comparison Slider
- Dedicated 8-Slide PowerPoint Presentation Export
"""

import os
import tempfile
import time
import json
import multiprocessing
# Set writable cache for matplotlib
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import streamlit as st
import numpy as np
import cv2
from PIL import Image

import image_processing as ip
import sequential_processing as seq
import parallel_processing as par
import visualization as viz
import utils
import geospatial_api as geo
import image_enhancement as enh

# ---------------------------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Satellite Change Detection | Parallel Computing & Live Earth Observation",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Geospatial Dark Theme CSS
CUSTOM_CSS = """
<style>
    /* Dark Navy Geospatial Background */
    .stApp {
        background-color: #0b132b;
        color: #edf2f4;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Top Title Header */
    .geo-header {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        border: 1px solid rgba(0, 245, 212, 0.25);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .geo-header h1 {
        color: #00f5d4;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin: 0;
        text-transform: uppercase;
    }
    .geo-header p {
        color: #8d99ae;
        font-size: 1.02rem;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Metric Cards */
    .metric-card {
        background: #1c2541;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #00f5d4;
        transform: translateY(-2px);
    }
    .metric-label {
        color: #8d99ae;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 4px 0;
        color: #edf2f4;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #06d6a0;
        font-weight: 500;
    }

    /* Accent color badges */
    .val-speedup { color: #00f5d4 !important; }
    .val-efficiency { color: #06d6a0 !important; }
    .val-sequential { color: #ef476f !important; }
    .val-parallel { color: #ffd166 !important; }

    /* Geospatial Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1c2541;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #8d99ae;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3a506b !important;
        color: #00f5d4 !important;
    }

    /* Sidebar Dark Customization */
    section[data-testid="stSidebar"] {
        background-color: #0d1b2a;
        border-right: 1px solid rgba(0, 245, 212, 0.15);
    }

    /* Primary Launch Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        color: #ffffff;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #00f5d4 0%, #00b4d8 100%);
        color: #0b132b;
        box-shadow: 0 0 15px rgba(0, 245, 212, 0.4);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "results_computed" not in st.session_state:
    st.session_state.results_computed = False
if "seq_res" not in st.session_state:
    st.session_state.seq_res = None
if "par_res" not in st.session_state:
    st.session_state.par_res = None
if "scaling_records" not in st.session_state:
    st.session_state.scaling_records = []
if "img_before" not in st.session_state:
    st.session_state.img_before = None
if "img_after" not in st.session_state:
    st.session_state.img_after = None
if "dataset_title" not in st.session_state:
    st.session_state.dataset_title = "Curated: Urban Expansion & Construction"
if "pool_warmed" not in st.session_state:
    try:
        par.get_or_create_pool(min(4, multiprocessing.cpu_count()))
        st.session_state.pool_warmed = True
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Header Section
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="geo-header">
        <h1>🛰️ SATELLITE CHANGE DETECTION SYSTEM</h1>
        <p>AI-Assisted Geospatial Analysis Using Parallel Multiprocessing &amp; Live Earth Observation</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Ingestion & Imagery Source")

    input_source = st.radio(
        "Image Source Selection",
        [
            "Curated Geospatial Datasets",
            "🌍 Live Google Maps & Landmark Explorer",
            "Upload Custom Satellite Images"
        ],
        index=0
    )

    available_samples = utils.get_available_samples()

    # Mode 1: Curated Datasets
    if input_source == "Curated Geospatial Datasets":
        sample_choice = st.selectbox(
            "Select Scenario",
            list(available_samples.keys()),
            index=0
        )
        sample_meta = available_samples[sample_choice]
        st.info(f"**Target Features:** {sample_meta['expected_changes']}\n\n**Resolution:** {sample_meta['resolution']} px")
        active_title = sample_choice

        if (st.session_state.img_before is None or
            st.session_state.dataset_title != active_title):
            st.session_state.img_before = utils.load_image_from_path(sample_meta["before"])
            st.session_state.img_after = utils.load_image_from_path(sample_meta["after"])
            st.session_state.dataset_title = active_title
            st.session_state.results_computed = False

    # Mode 2: Live Google Maps & Global Landmark Explorer
    elif input_source == "🌍 Live Google Maps & Landmark Explorer":
        st.markdown("#### Real-Time & Historical Satellite Imagery")
        geo_mode = st.radio("Satellite Query Mode", ["Global Landmark Historical Pairs", "Custom Coordinate Live Query"], index=0)

        if geo_mode == "Global Landmark Historical Pairs":
            preset_names = list(geo.GLOBAL_LANDMARK_PRESETS.keys())
            selected_preset = st.selectbox("Select Global Site", preset_names, index=0)
            p_info = geo.GLOBAL_LANDMARK_PRESETS[selected_preset]
            st.markdown(f"**Category:** `{p_info['category']}`")
            st.markdown(f"**Timeframes:** `{p_info['years'][0]}` vs `{p_info['years'][1]}`")
            st.caption(f"Coordinates: {p_info['lat']:.4f}° N, {p_info['lon']:.4f}° E (Zoom: {p_info['zoom']})")

            if st.button("🛰️ Load Landmark Satellite Pair", use_container_width=True):
                b_img, a_img, msg = geo.get_preset_satellite_imagery(selected_preset)
                if b_img is not None and a_img is not None:
                    st.session_state.img_before = b_img
                    st.session_state.img_after = a_img
                    st.session_state.dataset_title = f"Landmark: {selected_preset}"
                    st.session_state.results_computed = False
                    st.success(msg)

        else:
            st.markdown("##### 🛰️ Multi-Temporal Live Satellite Ingestion")
            st.caption("Direct connection to global satellite constellations & multi-year historical archives.")

            quick_loc = st.selectbox(
                "Quick Coordinate Presets",
                [
                    "Custom Coordinates",
                    "Tesla Gigafactory Texas (30.2223° N, -97.6171° W)",
                    "Dubai Palm Jumeirah (25.1124° N, 55.1390° E)",
                    "Lake Mead Hoover Dam (36.0506° N, -114.7377° W)",
                    "Beijing Daxing Mega Airport (39.5098° N, 116.4105° E)",
                    "London Olympic Park (51.5387° N, -0.0166° W)"
                ],
                index=1
            )

            if "Tesla" in quick_loc:
                def_lat, def_lon, def_zoom = 30.2223, -97.6171, 15
            elif "Dubai" in quick_loc:
                def_lat, def_lon, def_zoom = 25.1124, 55.1390, 14
            elif "Lake Mead" in quick_loc:
                def_lat, def_lon, def_zoom = 36.0506, -114.7377, 13
            elif "Beijing" in quick_loc:
                def_lat, def_lon, def_zoom = 39.5098, 116.4105, 13
            elif "London" in quick_loc:
                def_lat, def_lon, def_zoom = 51.5387, -0.0166, 15
            else:
                def_lat, def_lon, def_zoom = 25.1124, 55.1390, 14

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                c_lat = st.number_input("Latitude", value=def_lat, format="%.4f")
            with col_c2:
                c_lon = st.number_input("Longitude", value=def_lon, format="%.4f")

            c_zoom = st.slider("Satellite Zoom Level", 11, 17, def_zoom, help="Zoom 13: Regional view; Zoom 15: Building & road level (approx 1m resolution).")

            year_keys = list(geo.WAYBACK_CATALOG.keys())
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                t1_year = st.selectbox("Baseline Year (T1)", year_keys[:-1], index=0)
            with col_y2:
                t2_year = st.selectbox("Recent Year (T2)", year_keys, index=len(year_keys)-1)

            mosaic_size_label = st.select_slider("Live Mosaic Dimensions", options=["512 x 512 px (2x2 tiles)", "768 x 768 px (3x3 tiles)"], value="512 x 512 px (2x2 tiles)")
            grid_span = 3 if "768" in mosaic_size_label else 2

            google_key = st.text_input("Google Maps Static API Key (Optional)", type="password", help="If omitted, uses ArcGIS Multi-Temporal Earth Observation servers directly.")

            if st.button("🌐 Connect & Fetch Live Satellite Imagery", use_container_width=True):
                with st.spinner(f"Connecting to live orbital servers for {t1_year} vs {t2_year}..."):
                    live_t1, live_t2 = None, None
                    fetch_msg = ""

                    if google_key:
                        live_t2, g_msg = geo.fetch_google_maps_satellite(c_lat, c_lon, zoom=c_zoom, api_key=google_key)
                        if live_t2 is not None:
                            # Ingest historical archive for T1
                            live_t1, _ = geo.fetch_wayback_satellite_mosaic(c_lat, c_lon, zoom=c_zoom, m_id=geo.WAYBACK_CATALOG[t1_year]["m"], grid_span=grid_span)
                            fetch_msg = f"Live Google Maps & {t1_year} archive fetched."

                    if live_t1 is None or live_t2 is None:
                        live_t1, live_t2, fetch_msg = geo.fetch_realtime_and_historical_pair(
                            lat=c_lat,
                            lon=c_lon,
                            zoom=c_zoom,
                            hist_year_key=t1_year,
                            curr_year_key=t2_year,
                            grid_span=grid_span
                        )

                    if live_t1 is not None and live_t2 is not None:
                        st.session_state.img_before = live_t1
                        st.session_state.img_after = live_t2
                        st.session_state.dataset_title = f"Live Satellite: {quick_loc.split('(')[0].strip()} ({t1_year[:4]} vs {t2_year[:4]})"
                        st.session_state.results_computed = False
                        st.success(f"Connected! {fetch_msg}")
                    else:
                        st.error(f"Failed to fetch imagery: {fetch_msg}")

    # Mode 3: Custom Uploads
    else:
        st.markdown("#### Upload Satellite Images")
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            up_before = st.file_uploader("Before Image (T1)", type=["png", "jpg", "jpeg"])
        with col_up2:
            up_after = st.file_uploader("After Image (T2)", type=["png", "jpg", "jpeg"])

        if up_before is not None and up_after is not None:
            raw_b = utils.load_image_from_upload(up_before)
            raw_a = utils.load_image_from_upload(up_after)
            norm_b, norm_a = ip.resize_to_match(raw_b, raw_a)
            st.session_state.img_before = norm_b
            st.session_state.img_after = norm_a
            st.session_state.dataset_title = f"Custom: {up_before.name} vs {up_after.name}"
        else:
            st.warning("Please upload both Before and After satellite images.")

    st.markdown("---")
    st.markdown("### ⚡ Parallel Computing Setup")

    cpu_limit = multiprocessing.cpu_count()
    default_workers = min(4, cpu_limit)
    num_workers = st.slider(
        "CPU Worker Processes",
        min_value=1,
        max_value=cpu_limit,
        value=default_workers,
        help=f"Select number of concurrent CPU processes to distribute spatial image tiles. Detected system cores: {cpu_limit}"
    )

    grid_options = {
        "2 x 2 Grid (4 Tiles)": (2, 2),
        "3 x 3 Grid (9 Tiles)": (3, 3),
        "4 x 4 Grid (16 Tiles - Recommended)": (4, 4),
        "6 x 6 Grid (36 Tiles)": (6, 6),
        "8 x 8 Grid (64 Tiles)": (8, 8)
    }
    grid_choice = st.selectbox("Spatial Tile Grid", list(grid_options.keys()), index=2)
    grid_rows, grid_cols = grid_options[grid_choice]
    total_tiles = grid_rows * grid_cols

    seq_mode_choice = st.radio(
        "Sequential Baseline Mode",
        [
            "Tile-by-Tile Sequential (Apple-to-Apple Equivalence)",
            "Monolithic Full-Frame Sequential"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🔬 Detection & Radiometric Enhancement")

    diff_mode = st.selectbox(
        "Processing Pipeline Mode",
        [
            "Deep Structural & Bilateral Analysis",
            "Color-Aware Absolute Difference",
            "Structural Edge Difference",
            "Grayscale Difference"
        ],
        index=0
    )

    threshold_type = st.selectbox(
        "Thresholding Method",
        ["Otsu Automatic", "Manual Threshold", "Adaptive Gaussian"],
        index=0
    )

    manual_thresh_val = 35
    if threshold_type == "Manual Threshold":
        manual_thresh_val = st.slider("Manual Threshold Cutoff", 5, 120, 35)

    with st.expander("✨ Radiometric & Image Quality Controls"):
        opt_hist_match = st.checkbox("Radiometric Normalization (Histogram Match)", value=True, help="Warps CDF of Time T2 to match Time T1, neutralizing seasonal sun angle and atmospheric lighting shifts.")
        opt_clahe = st.checkbox("Apply CLAHE Contrast Boost", value=True, help="Contrast Limited Adaptive Histogram Equalization on Luminance channel.")
        opt_unsharp = st.checkbox("Super-Resolution Unsharp Masking", value=True, help="Edge accentuation for crisp building boundaries and roads.")
        opt_dehaze = st.checkbox("Atmospheric Dehazing (Dark Channel Prior)", value=False, help="Removes aerosol scattering and cloud haze.")
        opt_subpixel = st.checkbox("Sub-Pixel Geometric Alignment (ECC)", value=False, help="Enhanced Correlation Coefficient maximization for sub-pixel accuracy.")
        blur_kernel = st.select_slider("Bilateral / Smoothing Kernel", options=[3, 5, 7, 9], value=7)
        morph_kernel = st.select_slider("Morphological Cleanup Kernel", options=[1, 3, 5, 7], value=3)
        min_region_area = st.slider("Min Cluster Size Filter (px²)", 10, 500, 60, step=10)

    st.markdown("---")
    if st.button("🔄 Reset Analysis State", use_container_width=True):
        st.session_state.results_computed = False
        st.session_state.seq_res = None
        st.session_state.par_res = None
        st.session_state.scaling_records = []
        st.rerun()


# ---------------------------------------------------------------------------
# Main Application Content
# ---------------------------------------------------------------------------
if st.session_state.img_before is None or st.session_state.img_after is None:
    st.info("👈 Please select a curated sample dataset, explore Google Maps live imagery, or upload images from the sidebar.")
    st.stop()

raw_before = st.session_state.img_before.copy()
raw_after = st.session_state.img_after.copy()

# Pre-processing & Radiometric Pipeline
before_img = raw_before
after_img = raw_after

# 1. Sub-pixel ECC Alignment if selected
if 'opt_subpixel' in locals() and opt_subpixel:
    with st.spinner("Computing sub-pixel ECC geometric co-registration..."):
        aligned_after, success = enh.align_subpixel_ecc(before_img, after_img)
        if success:
            after_img = aligned_after

# 2. Dehaze
if 'opt_dehaze' in locals() and opt_dehaze:
    before_img = enh.apply_atmospheric_dehaze(before_img)
    after_img = enh.apply_atmospheric_dehaze(after_img)

# 3. Radiometric Histogram Matching (Neutralizes seasonal lighting)
if 'opt_hist_match' in locals() and opt_hist_match:
    after_img = enh.match_histograms_radiometric(after_img, before_img)

# 4. CLAHE Contrast Boost
if 'opt_clahe' in locals() and opt_clahe:
    before_img = enh.apply_clahe_enhancement(before_img)
    after_img = enh.apply_clahe_enhancement(after_img)

# 5. Super-Resolution Unsharp Masking
if 'opt_unsharp' in locals() and opt_unsharp:
    before_img = enh.apply_unsharp_mask(before_img)
    after_img = enh.apply_unsharp_mask(after_img)

h_img, w_img = before_img.shape[:2]


# ---------------------------------------------------------------------------
# Section 1: Satellite Image Inspection (Side-by-Side)
# ---------------------------------------------------------------------------
st.markdown("### 1. Satellite Imagery Overview")
st.markdown(f"**Target Site:** `{st.session_state.dataset_title}` &nbsp;|&nbsp; **Resolution:** `{w_img} × {h_img} px` ({w_img * h_img:,} pixels)")

col_img1, col_img2 = st.columns(2)
with col_img1:
    st.markdown("##### 📅 Reference Image (Time T1 - Historical Baseline)")
    st.image(before_img, use_container_width=True, caption=f"T1 Baseline Reference ({w_img}x{h_img})")

with col_img2:
    st.markdown("##### 📅 Current Image (Time T2 - Observation Scene)")
    st.image(after_img, use_container_width=True, caption=f"T2 Current Scene ({w_img}x{h_img})")


# ---------------------------------------------------------------------------
# Action Bar: Trigger Analysis
# ---------------------------------------------------------------------------
st.markdown("---")
col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    run_benchmark = st.button("🚀 RUN CHANGE DETECTION BENCHMARK (Sequential vs Parallel)", use_container_width=True)

with col_btn2:
    run_scaling = st.button("📈 Run Multi-Core Scaling Curve (1 to 8 Cores)", use_container_width=True)


# ---------------------------------------------------------------------------
# Execution Logic
# ---------------------------------------------------------------------------
if run_benchmark:
    prog_bar = st.progress(0.0)
    status_text = st.empty()

    # Step 1: Sequential Run
    status_text.markdown("⏳ **Running Sequential Processing (Single Core)...**")
    if "Tile-by-Tile" in seq_mode_choice:
        seq_res = seq.run_sequential_tiled_detection(
            before_img=before_img,
            after_img=after_img,
            grid_rows=grid_rows,
            grid_cols=grid_cols,
            diff_mode=diff_mode,
            blur_kernel=blur_kernel,
            threshold_type=threshold_type,
            manual_threshold=manual_thresh_val,
            morph_kernel=morph_kernel,
            min_area=min_region_area,
            progress_callback=lambda p, msg: prog_bar.progress(p * 0.45)
        )
    else:
        seq_res = seq.run_sequential_change_detection(
            before_img=before_img,
            after_img=after_img,
            diff_mode=diff_mode,
            blur_kernel=blur_kernel,
            threshold_type=threshold_type,
            manual_threshold=manual_thresh_val,
            morph_kernel=morph_kernel,
            min_area=min_region_area,
            progress_callback=lambda p, msg: prog_bar.progress(p * 0.45)
        )

    prog_bar.progress(0.50)
    status_text.markdown(f"⏳ **Dispatching Parallel Processing across {num_workers} CPU Workers ({total_tiles} tiles)...**")

    # Step 2: Parallel Run
    par_res = par.run_parallel_change_detection(
        before_img=before_img,
        after_img=after_img,
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        num_processes=num_workers,
        diff_mode=diff_mode,
        blur_kernel=blur_kernel,
        threshold_type=threshold_type,
        manual_threshold=manual_thresh_val,
        morph_kernel=morph_kernel,
        min_area=min_region_area,
        progress_callback=lambda p, msg: prog_bar.progress(0.50 + p * 0.48)
    )

    prog_bar.progress(1.0)
    status_text.success("✅ Analysis completed successfully!")
    time.sleep(0.3)
    status_text.empty()
    prog_bar.empty()

    st.session_state.seq_res = seq_res
    st.session_state.par_res = par_res
    st.session_state.results_computed = True


if run_scaling:
    scaling_bar = st.progress(0.0)
    scaling_status = st.empty()
    test_cores = [1, 2, 4]
    if cpu_limit >= 8:
        test_cores.append(8)
    if cpu_limit >= 16:
        test_cores.append(16)

    scaling_records = []
    scaling_status.markdown("Benchmarking 1 Core...")
    r1 = par.run_parallel_change_detection(
        before_img, after_img, grid_rows, grid_cols, num_processes=1,
        diff_mode=diff_mode, blur_kernel=blur_kernel, threshold_type=threshold_type,
        manual_threshold=manual_thresh_val, morph_kernel=morph_kernel, min_area=min_region_area
    )
    t_base = r1["execution_time"]
    scaling_records.append({"cores": 1, "time": t_base, "speedup": 1.0, "efficiency": 100.0})

    for idx, c in enumerate(test_cores[1:], 1):
        scaling_status.markdown(f"Benchmarking {c} Cores...")
        scaling_bar.progress(idx / len(test_cores))
        rc = par.run_parallel_change_detection(
            before_img, after_img, grid_rows, grid_cols, num_processes=c,
            diff_mode=diff_mode, blur_kernel=blur_kernel, threshold_type=threshold_type,
            manual_threshold=manual_thresh_val, morph_kernel=morph_kernel, min_area=min_region_area
        )
        tc = rc["execution_time"]
        sp = t_base / tc if tc > 0 else 1.0
        eff = (sp / c) * 100.0
        scaling_records.append({"cores": c, "time": tc, "speedup": sp, "efficiency": eff})

    scaling_bar.progress(1.0)
    scaling_status.success("✅ Multi-Core Scaling Benchmark complete!")
    time.sleep(0.3)
    scaling_status.empty()
    scaling_bar.empty()

    st.session_state.scaling_records = scaling_records


# ---------------------------------------------------------------------------
# Results Display
# ---------------------------------------------------------------------------
if st.session_state.results_computed and st.session_state.seq_res and st.session_state.par_res:
    seq_res = st.session_state.seq_res
    par_res = st.session_state.par_res

    t_seq = seq_res["execution_time"]
    t_par = par_res["execution_time"]
    speedup = t_seq / t_par if t_par > 0 else 1.0
    efficiency = (speedup / num_workers) * 100.0
    metrics = par_res["metrics"]

    # Top Metric Dashboard Cards
    st.markdown("### 2. Performance & Geospatial Metrics")
    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

    with m_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Sequential Time</div>
                <div class="metric-value val-sequential">{t_seq:.3f} s</div>
                <div class="metric-sub">Single Process</div>
            </div>
            """, unsafe_allow_html=True
        )

    with m_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Parallel Time</div>
                <div class="metric-value val-parallel">{t_par:.3f} s</div>
                <div class="metric-sub">{num_workers} Workers / {total_tiles} Tiles</div>
            </div>
            """, unsafe_allow_html=True
        )

    with m_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Speedup Factor</div>
                <div class="metric-value val-speedup">{speedup:.2f}x</div>
                <div class="metric-sub">T_seq / T_par</div>
            </div>
            """, unsafe_allow_html=True
        )

    with m_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Parallel Efficiency</div>
                <div class="metric-value val-efficiency">{efficiency:.1f}%</div>
                <div class="metric-sub">Speedup / {num_workers} Cores</div>
            </div>
            """, unsafe_allow_html=True
        )

    with m_col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Surface Changed</div>
                <div class="metric-value">{metrics['change_percentage']:.2f}%</div>
                <div class="metric-sub">{metrics['changed_pixels']:,} Pixels</div>
            </div>
            """, unsafe_allow_html=True
        )

    with m_col6:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Detected Regions</div>
                <div class="metric-value">{metrics['region_count']}</div>
                <div class="metric-sub">Contiguous Parcels</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Multi-Class Semantic Change Analytics
    semantic_data = enh.classify_change_categories(before_img, after_img, par_res["binary_mask"])

    # 7 Comprehensive Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Detected Changes Overlay",
        "🏷️ Multi-Class Semantic Analytics",
        "↔️ Interactive Swipe Comparison",
        "📊 Parallel Computing Analysis",
        "🔥 Difference Heatmap & Mask",
        "🧩 Tile Grid Decomposition",
        "📑 Executive Report & Export"
    ])

    # Tab 1: Final Highlighted Overlay
    with tab1:
        st.markdown("#### High-Contrast Change Detection Overlay")
        st.markdown("Detected geographical alterations highlighted with vibrant alpha overlays and bounding box region tags.")

        overlay_img = ip.generate_change_overlay(
            base_image=after_img,
            mask=par_res["binary_mask"],
            overlay_color=(255, 30, 30),
            alpha=0.45,
            draw_bounding_boxes=True,
            draw_contours=True,
            box_color=(0, 240, 255),
            min_box_area=min_region_area
        )

        st.image(overlay_img, use_container_width=True, caption=f"Annotated Change Overlay ({metrics['region_count']} detected clusters)")

        overlay_bytes = utils.numpy_to_download_bytes(overlay_img)
        st.download_button(
            label="💾 Download Change Overlay Image (PNG)",
            data=overlay_bytes,
            file_name=f"satellite_change_overlay_{int(time.time())}.png",
            mime="image/png"
        )

    # Tab 2: Semantic Multi-Class Categorization
    with tab2:
        st.markdown("#### 🏷️ Multi-Class Semantic Categorization")
        st.markdown("Distinguishes between **New Construction**, **Vegetation Loss**, **Water Dynamics**, and **Road Infrastructure** using spectral VARI and structural edge gradients.")

        col_cat_img, col_cat_pie = st.columns([3, 2])
        with col_cat_img:
            st.image(semantic_data["category_overlay"], use_container_width=True, caption="Categorized Change Map: 🔴 Red = Construction | 🟢 Green = Vegetation Loss | 🔵 Blue = Water Dynamics | 🟡 Gold = Roads & Soil")
        with col_cat_pie:
            fig_pie = viz.create_semantic_breakdown_pie(semantic_data["percentages"])
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("##### Quantitative Class Breakdown")
            for cat_name, cnt in semantic_data["counts"].items():
                pct = semantic_data["percentages"][cat_name]
                st.write(f"• **{cat_name}:** {cnt:,} pixels ({pct:.1f}%)")

    # Tab 3: Interactive Swipe Comparison Slider
    with tab3:
        st.markdown("#### ↔️ Interactive Swipe Comparison Slider")
        st.markdown("Drag the central divider left or right to inspect the seamless spatial transition between Historical T1 and Current T2 imagery.")
        swipe_html = viz.create_interactive_swipe_html(before_img, after_img)
        st.components.v1.html(swipe_html, height=530)

    # Tab 4: Parallel Computing Performance
    with tab4:
        st.markdown("#### Parallel Computing Performance Analysis")

        col_chart1, col_chart2 = st.columns([3, 2])
        with col_chart1:
            fig_bar = viz.create_execution_comparison_chart(t_seq, t_par, num_workers, total_tiles)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            fig_gauge = viz.create_speedup_efficiency_gauges(speedup, efficiency, num_workers)
            st.plotly_chart(fig_gauge, use_container_width=True)

        if st.session_state.scaling_records:
            st.markdown("---")
            st.markdown("#### Multi-Core Strong Scaling Curve (Amdahl's Law)")
            col_sc1, col_sc2 = st.columns([3, 2])
            with col_sc1:
                fig_scale = viz.create_scaling_comparison_chart(st.session_state.scaling_records)
                st.plotly_chart(fig_scale, use_container_width=True)
            with col_sc2:
                st.markdown("##### Scaling Benchmark Records")
                st.dataframe(st.session_state.scaling_records, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🔬 Technical Explanation: Parallel vs Sequential Execution")

        if speedup >= 1.2:
            st.success(
                f"**Performance Gain Verified:** Parallel multiprocessing achieved a **{speedup:.2f}x speedup**, "
                f"reducing execution time from **{t_seq:.3f}s** down to **{t_par:.3f}s** (a **{((t_seq - t_par) / t_seq)*100:.1f}%** reduction). "
                f"Distributing the {total_tiles} spatial tiles across {num_workers} CPU worker processes allowed simultaneous bilateral filtering, "
                f"Sobel gradient magnitude calculations, and thresholding."
            )
        else:
            st.info(
                f"**Amdahl's Law & Granularity Tradeoff:** Measured speedup is **{speedup:.2f}x**. "
                f"In Python multiprocessing, inter-process communication (IPC) serialization and subprocess spawning have a fixed time overhead."
            )

    # Tab 5: Heatmap & Binary Mask
    with tab5:
        st.markdown("#### Intermediate Change Maps")
        col_hm, col_bm = st.columns(2)

        diff_heatmap = ip.generate_diff_heatmap(par_res["diff_map"])

        with col_hm:
            st.markdown("##### 🔥 Radiometric Difference Heatmap")
            st.image(diff_heatmap, use_container_width=True, caption="Inferno Colormap: High intensity indicates significant spectral/structural deviation")

        with col_bm:
            st.markdown("##### 🏁 Cleaned Binary Change Mask")
            st.image(par_res["binary_mask"], use_container_width=True, caption="Binary Mask (255 = Changed Area, 0 = Unchanged Ground)")

        col_donut, col_stats = st.columns([1, 1])
        with col_donut:
            fig_donut = viz.create_surface_change_donut(metrics["total_pixels"], metrics["changed_pixels"])
            st.plotly_chart(fig_donut, use_container_width=True)
        with col_stats:
            st.markdown("##### 📐 Quantitative Spatial Summary")
            st.write({
                "Total Ground Pixels": f"{metrics['total_pixels']:,}",
                "Changed Pixels": f"{metrics['changed_pixels']:,}",
                "Surface Modification %": f"{metrics['change_percentage']:.3f}%",
                "Contiguous Change Parcels": metrics["region_count"],
                "Average Parcel Area": f"{metrics['mean_region_size']:.1f} px²"
            })

    # Tab 6: Tile Grid Decomposition
    with tab6:
        st.markdown("#### Spatial Tile Decomposition & Worker Distribution")
        st.markdown(f"The satellite image was partitioned into a **{grid_rows} × {grid_cols} grid ({total_tiles} non-overlapping tiles)**.")

        grid_vis = ip.draw_tile_grid_overlay(after_img, par_res["tile_info"])
        st.image(grid_vis, use_container_width=True, caption=f"Spatial Tile Grid ({total_tiles} Tiles Distributed Across {num_workers} Workers)")

        tile_rows = []
        for t in par_res["tile_info"]:
            tid = t["tile_id"]
            y1, y2, x1, x2 = t["bbox"]
            cnt = t["changed_count"]
            t_area = (y2 - y1) * (x2 - x1)
            pct = (cnt / t_area) * 100.0 if t_area > 0 else 0.0
            tile_rows.append({
                "Tile ID": f"Tile #{tid}",
                "Coordinates (Y1, Y2, x1, x2)": f"({y1}, {y2}, {x1}, {x2})",
                "Tile Size": f"{x2-x1}x{y2-y1} px",
                "Changed Pixels": f"{cnt:,}",
                "Tile Change %": f"{pct:.2f}%"
            })

        st.dataframe(tile_rows, use_container_width=True, height=280)

    # Tab 7: Executive Report & Export
    with tab7:
        st.markdown("#### Technical Report & Geospatial Export")

        report_md = utils.generate_markdown_report(
            dataset_name=st.session_state.dataset_title,
            img_shape=(h_img, w_img),
            diff_mode=diff_mode,
            threshold_type=threshold_type,
            seq_res=seq_res,
            par_res=par_res,
            speedup=speedup,
            efficiency=efficiency
        )

        st.markdown(report_md)

        st.markdown("---")
        st.markdown("##### 📥 Export Analysis Artifacts")
        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)

        with col_dl1:
            st.download_button(
                label="📄 Download Report (.md)",
                data=report_md,
                file_name=f"satellite_change_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_dl2:
            poster_img = viz.generate_composite_report_image(
                before_img=before_img,
                after_img=after_img,
                diff_heatmap=diff_heatmap,
                binary_mask=par_res["binary_mask"],
                overlay_img=overlay_img,
                metrics=metrics,
                speedup=speedup,
                efficiency=efficiency,
                seq_time=t_seq,
                par_time=t_par,
                num_processes=num_workers
            )
            poster_bytes = utils.numpy_to_download_bytes(poster_img)
            st.download_button(
                label="🖼️ Download 5-Panel Poster",
                data=poster_bytes,
                file_name=f"satellite_poster_{int(time.time())}.png",
                mime="image/png",
                use_container_width=True
            )

        with col_dl3:
            geojson_data = {
                "metadata": {
                    "dataset": st.session_state.dataset_title,
                    "resolution": f"{w_img}x{h_img}",
                    "speedup": speedup,
                    "efficiency": efficiency
                },
                "changed_regions": metrics["bounding_boxes"]
            }
            st.download_button(
                label="🌐 Export Parcels (.json)",
                data=json.dumps(geojson_data, indent=2),
                file_name=f"change_regions_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_dl4:
            pptx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parallel_satellite_change_detection.pptx")
            if os.path.exists(pptx_path):
                with open(pptx_path, "rb") as f_ppt:
                    st.download_button(
                        label="📊 Download 8-Slide PPT (.pptx)",
                        data=f_ppt.read(),
                        file_name="parallel_satellite_change_detection.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )

        st.markdown("---")
        st.markdown("##### 🎬 Looping Satellite Time-Lapse (Animated GIF)")
        st.caption("Auto-generated multi-phase animation cycling through Prior Scene (T1), Recent Scene (T2), and Detected Change Annotations.")
        col_gif_view, col_gif_action = st.columns([2, 1])
        gif_bytes = utils.create_satellite_timelapse_gif(
            img_before=before_img,
            img_after=after_img,
            img_overlay=overlay_img,
            diff_heatmap=diff_heatmap
        )
        with col_gif_view:
            st.image(gif_bytes, caption="Satellite Temporal Loop (Before → After → Detected Changes)", use_container_width=True)
        with col_gif_action:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Animated GIF",
                data=gif_bytes,
                file_name=f"satellite_timelapse_{int(time.time())}.gif",
                mime="image/gif",
                use_container_width=True
            )
            st.info("💡 Useful for executive briefings, portfolio showcases, and technical slide embeds.")


# ---------------------------------------------------------------------------
# Section 8: Accuracy & Geospatial Limitations Disclosure
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️ Accuracy, Methodology & Geospatial Limitations Disclosure"):
    st.markdown(
        """
        **Important Geospatial Engineering Disclosure:**
        - **Visual & Radiometric Differencing vs Object AI:**  
          This system implements high-performance pixel differencing, structural gradient analysis (Sobel/Laplacian), and morphological clustering.  
          It accurately flags **visual, spectral, and radiometric deviations** between co-registered satellite images.
        - **Semantic Understanding:**  
          The system detects that ground pixels have changed significantly (e.g. from vegetated green canopy to bare earth or reflective building material). However, it does not independently classify whether a change is specifically a hospital, school, or residential building without a secondary semantic classification neural network (e.g., DeepLabV3, Mask R-CNN, or YOLO).
        - **Co-registration Requirement:**  
          Accurate differencing assumes both satellite images have been ortho-rectified and geographically co-registered. Minor misalignment can lead to false edge artifacts, which can be mitigated via the optional sub-pixel ECC alignment and ORB feature matching tools.
        """
    )
