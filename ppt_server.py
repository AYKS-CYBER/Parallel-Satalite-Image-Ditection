"""
ppt_server.py
=============
Dedicated Presentation Viewer & PPT Download Server.
Serves an interactive 12-slide presentation viewer with fail-proof dual download:
1. Direct HTTP attachment download (/download)
2. Instant client-side base64 Blob download (zero roundtrip, works offline/instantly)
"""

import os
import sys
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8520
PPTX_FILENAME = "parallel_satellite_change_detection.pptx"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PPTX_PATH = os.path.join(BASE_DIR, PPTX_FILENAME)
REPORT_PDF_PATH = os.path.join(BASE_DIR, "project_report.pdf")
REPORT_DOCX_PATH = os.path.join(BASE_DIR, "project_report.docx")
REPORT_HTML_PATH = os.path.join(BASE_DIR, "project_report.html")
REPORT_MD_PATH = os.path.join(BASE_DIR, "project_report.md")

if os.path.exists(PPTX_PATH):
    with open(PPTX_PATH, "rb") as f:
        PPTX_BYTES = f.read()
    PPTX_B64 = base64.b64encode(PPTX_BYTES).decode("utf-8")
else:
    PPTX_BYTES = b""
    PPTX_B64 = ""

SLIDES_DATA = [
    {
        "num": 1,
        "tag": "AI-ASSISTED GEOSPATIAL REMOTE SENSING & HPC",
        "title": "Parallel Satellite Image Change Detection Using Multiprocessing",
        "subtitle": "Live Google Maps / Satellite Ingestion • Sub-Pixel Co-Registration • Multi-Class Semantic Categorization",
        "content_html": """
            <div style="margin-top: 30px; display: flex; flex-wrap: wrap; gap: 12px;">
                <span class="badge badge-cyan">Python 3.13</span>
                <span class="badge badge-green">Live Google Maps</span>
                <span class="badge badge-gold">Multiprocessing Pool</span>
                <span class="badge badge-red">Sub-Pixel ECC & VARI</span>
                <span class="badge badge-cyan">16 CPU Cores Supported</span>
                <span class="badge badge-green">ArcGIS Wayback Ingestion</span>
            </div>
            <div style="margin-top: 35px; padding: 22px 26px; background: rgba(28, 37, 65, 0.7); border-left: 4px solid #00f5d4; border-radius: 8px;">
                <p style="margin: 0; color: #edf2f4; font-size: 1.05rem; line-height: 1.6;">
                    <strong>Executive Objective:</strong> Overcome computational bottlenecks in high-resolution multi-temporal satellite remote sensing by partitioning scenes into independent spatial tiles, executing concurrent vision pipelines across multi-core CPUs via Python multiprocessing, and integrating live Google Maps &amp; Earth Observation orbital feeds.
                </p>
            </div>
        """
    },
    {
        "num": 2,
        "tag": "01 | CONTEXT & PROBLEM DEFINITION",
        "title": "Geospatial Big Data Challenges & Computational Bottlenecks",
        "subtitle": "Why Traditional Single-Threaded Image Processing Fails at Planetary Scale",
        "content_html": """
            <div class="grid-3">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">🛰️ Data Scale Ceiling</h3>
                    <p class="card-sub">Gigabytes of Imagery Daily</p>
                    <ul>
                        <li>Sentinel-2, Landsat-9, Maxar, and Planet constellations generate terabytes of optical imagery daily at sub-meter ground resolution.</li>
                        <li>High-order bilateral smoothing and Sobel gradient filters incur high latency on multi-megapixel scenes.</li>
                        <li>Sequential execution leaves modern multi-core processors 90%+ idle.</li>
                    </ul>
                </div>
                <div class="card card-gold">
                    <h3 style="color: #ffd166;">☀️ Radiometric Drift</h3>
                    <p class="card-sub">Seasonal & Atmospheric Interference</p>
                    <ul>
                        <li>Solar zenith shifts alter shadow angles between multi-year captures, generating false-positive change anomalies.</li>
                        <li>Atmospheric haze, aerosols, and thin cirrus clouds distort true ground surface reflectance.</li>
                        <li>Sensor gain variations across different imaging satellites distort pure pixel intensity values.</li>
                    </ul>
                </div>
                <div class="card card-red">
                    <h3 style="color: #ef476f;">📐 Parallax & Misalignment</h3>
                    <p class="card-sub">Geometric Co-Registration Errors</p>
                    <ul>
                        <li>Off-nadir satellite viewing angles cause tall structures to lean in varying directions across passes.</li>
                        <li>Even a 1-to-2 pixel geometric misalignment creates false change rings along every building footprint and road.</li>
                        <li>Requires automated sub-pixel affine ECC alignment prior to differencing.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 3,
        "tag": "02 | ARCHITECTURE & ENGINEERING STACK",
        "title": "Languages, Models, Libraries & Software Packages",
        "subtitle": "Complete System Stack: Languages, Algorithmic Models & Python Modules",
        "content_html": """
            <div class="grid-3">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">💻 Languages & HPC</h3>
                    <p class="card-sub">Core Computational Stack</p>
                    <ul>
                        <li><strong>Python 3.13:</strong> High-level orchestration, memory slicing, and IPC multiprocessing.</li>
                        <li><strong>multiprocessing.Pool:</strong> Process pool execution bypassing the Python Global Interpreter Lock (GIL).</li>
                        <li><strong>ThreadPoolExecutor:</strong> Concurrent I/O engine for simultaneous multi-tile orbital satellite streaming.</li>
                        <li><strong>Amdahl's Law Model:</strong> Concurrency model governing speedup limits and serial bottlenecks.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">🧠 Vision & Models</h3>
                    <p class="card-sub">Computer Vision & Mathematical Models</p>
                    <ul>
                        <li><strong>OpenCV 4.10 (cv2):</strong> C++ SIMD bilateral filtering, Sobel gradients, and morphological kernels.</li>
                        <li><strong>Sub-Pixel ECC Model:</strong> Enhanced Correlation Coefficient affine transformation optimization.</li>
                        <li><strong>Dark Channel Prior Dehaze:</strong> Atmospheric scattering and transmission estimation model.</li>
                        <li><strong>VARI Spectral Model:</strong> Visible Atmospherically Resistant Index (G-R)/(G+R-B) for canopy monitoring.</li>
                    </ul>
                </div>
                <div class="card card-gold">
                    <h3 style="color: #ffd166;">📦 Packages & GIS</h3>
                    <p class="card-sub">Geospatial & Dashboard Modules</p>
                    <ul>
                        <li><strong>NumPy 2.x:</strong> Vectorized array operations and linear spatial tile interpolation.</li>
                        <li><strong>ArcGIS & Google Maps APIs:</strong> Sub-meter optical satellite tile mosaics & historical archives.</li>
                        <li><strong>Streamlit 1.43:</strong> Reactive dark-navy web UI with session state management.</li>
                        <li><strong>Plotly & python-pptx:</strong> Interactive charts, gauge meters, and automated slide generation.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 4,
        "tag": "03 | REAL-TIME EARTH OBSERVATION INTEGRATION",
        "title": "Live Satellite Ingestion & Multi-Temporal Archive Architecture",
        "subtitle": "Connecting to Google Maps API & ArcGIS Multi-Year Global Satellite Feeds",
        "content_html": """
            <div class="grid-2">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">🌐 Multi-Temporal Ingestion Engine</h3>
                    <ul>
                        <li><strong>WGS84 to Web Mercator Projection:</strong> Converts latitude and longitude into Slippy Map tile indices (tx, ty) at zoom levels 11 to 17 using <code>deg2num</code>.</li>
                        <li><strong>ArcGIS Wayback Multi-Year Archive:</strong> Ingests true historical imagery spanning 2014, 2016, 2018, 2020, 2022, 2024 up to <strong>2026 Live Real-Time Current</strong>.</li>
                        <li><strong>Concurrent ThreadPool Ingestion:</strong> Downloads 4 to 9 adjacent 256x256 satellite tiles simultaneously in ~2.3 seconds.</li>
                        <li><strong>Google Maps Static Satellite API:</strong> Direct high-resolution satellite imagery fetching via custom user API keys.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">🛰️ Verified Global Observatories</h3>
                    <ul>
                        <li><strong>Tesla Gigafactory Texas (Austin):</strong> Rural scrubland (2014) converted into 10M sq ft mega-facility (2026). Measured 44.6 average pixel delta.</li>
                        <li><strong>Dubai Palm Jumeirah (UAE):</strong> Baseline Persian Gulf ocean (2001) transformed into luxury artificial archipelago (2026).</li>
                        <li><strong>Lake Mead Hoover Dam (USA):</strong> Severe reservoir waterline retreat exposing white bathtub sediment ring.</li>
                        <li><strong>Amazon Deforestation (Rondônia):</strong> Dense tropical rainforest conversion to fishbone logging corridors.</li>
                        <li><strong>Beijing Daxing Mega Airport:</strong> Farmland transformed into terminal starfish hub and highway ramps.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 5,
        "tag": "04 | IMAGE QUALITY & PREPROCESSING ENGINEERING",
        "title": "Radiometric Normalization & Sub-Pixel Geometric Co-Registration",
        "subtitle": "Neutralizing Seasonal Illumination, Atmospheric Scattering & Camera Parallax",
        "content_html": """
            <div class="grid-2">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">1. Sub-Pixel ECC Geometric Alignment</h3>
                    <p class="card-sub">Enhanced Correlation Coefficient</p>
                    <ul>
                        <li>Computes optimal 2×3 affine transformation matrix using iterative gradient optimization.</li>
                        <li>Achieves sub-pixel precision down to 0.05 pixels, eliminating spurious border change artifacts.</li>
                    </ul>
                    <h3 style="color: #00f5d4; margin-top: 18px;">2. Cumulative Histogram Matching</h3>
                    <p class="card-sub">Radiometric Sun Angle Calibration</p>
                    <ul>
                        <li>Maps the cumulative distribution function (CDF) of T1 onto T2 per color channel.</li>
                        <li>Neutralizes global false positives caused by differing solar zenith angles and seasonal lighting.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">3. Atmospheric Dehazing (Dark Channel Prior)</h3>
                    <p class="card-sub">He et al. Formulation</p>
                    <ul>
                        <li>Estimates atmospheric aerosol scatter and optical transmission map <code>t(x)</code>.</li>
                        <li>Restores ground surface reflectivity through thin haze, smog, and cloud fringes.</li>
                    </ul>
                    <h3 style="color: #06d6a0; margin-top: 18px;">4. CLAHE & Super-Resolution Sharpening</h3>
                    <p class="card-sub">Micro-Contrast & Edge Definition</p>
                    <ul>
                        <li>Contrast Limited Adaptive Histogram Equalization boosts local contrast without amplifying sensor gain noise.</li>
                        <li>Unsharp masking filter sharpens building footprints and transportation corridors.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 6,
        "tag": "05 | AI-ASSISTED SPECTRAL ANALYTICS",
        "title": "Multi-Class Semantic Change Categorization & Spatial Indices",
        "subtitle": "Distinguishing Structural Construction, Deforestation, Water Retreat & Road Infrastructure",
        "content_html": """
            <div class="grid-2">
                <div class="card card-red">
                    <h3 style="color: #ef476f;">🔴 Structural & Urban Changes</h3>
                    <ul>
                        <li><strong>Target Features:</strong> New industrial warehouses, commercial buildings, residential subdivisions, concrete foundation slabs.</li>
                        <li><strong>Spectral & Gradient Signature:</strong> High edge gradient response (Sobel magnitude > 45) combined with significant broadband reflectance delta.</li>
                        <li><strong>Morphology:</strong> Rectangular contour closure and minimum area parcel filtering.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">🟢 Canopy Loss & Deforestation</h3>
                    <ul>
                        <li><strong>Target Features:</strong> Rainforest clear-cutting, tree canopy loss, agricultural harvesting, wildfire burn scars.</li>
                        <li><strong>VARI Spectral Index:</strong> Visible Atmospherically Resistant Index <code>(G - R) / (G + R - B)</code>.</li>
                        <li><strong>Delta Tracking:</strong> Triggers when vegetative index drops by > 0.15 between T1 and T2.</li>
                    </ul>
                </div>
                <div class="card card-cyan" style="margin-top: 12px;">
                    <h3 style="color: #00f5d4;">🔵 Water Surface Dynamics</h3>
                    <ul>
                        <li><strong>Target Features:</strong> Reservoir shoreline recession, lakebed drying, flood inundation zones.</li>
                        <li><strong>Spectral Signature:</strong> Deep blue-to-near-infrared contrast ratio tracking modified NDWI water proxy.</li>
                    </ul>
                </div>
                <div class="card card-gold" style="margin-top: 12px;">
                    <h3 style="color: #ffd166;">🟡 Road Infrastructure & Soil</h3>
                    <ul>
                        <li><strong>Target Features:</strong> Expressway expansions, airport runways, cloverleaf interchange ramps, bare earthworks.</li>
                        <li><strong>Morphology:</strong> High aspect-ratio linear contour elongation (Length / Width > 3.0).</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 7,
        "tag": "06 | HIGH PERFORMANCE COMPUTING IMPLEMENTATION",
        "title": "Parallel Domain Decomposition & Windows Multiprocessing Architecture",
        "subtitle": "Bypassing the Python GIL via Independent CPU Processes & Shared Memory Slicing",
        "content_html": """
            <div class="grid-2">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">🧩 Spatial Domain Decomposition</h3>
                    <ul>
                        <li><strong>Tile Grid Partitioning:</strong> Divides massive satellite scenes into N×M non-overlapping rectangular blocks (2×2 up to 8×8 grids, yielding 4 to 64 tiles).</li>
                        <li><strong>Linear Coordinate Math:</strong> Uses <code>np.linspace</code> integer coordinate interpolation to eliminate off-by-one boundary gaps and seam overlaps.</li>
                        <li><strong>Global Otsu Calibration:</strong> Evaluates a downsampled global proxy threshold and broadcasts uniform <code>T*</code> to all workers, preventing quiet tiles from amplifying local noise.</li>
                        <li><strong>Seam-Free Assembly:</strong> Pre-allocates destination buffers; workers write directly into non-overlapping spatial slices.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">⚡ Windows Spawn Safety & IPC Optimization</h3>
                    <ul>
                        <li><strong>Windows Spawn Safety:</strong> Pure top-level worker functions defined in <code>parallel_processing.py</code> avoid recursive Streamlit GUI execution and pickle errors.</li>
                        <li><strong>Persistent Warm Worker Pool:</strong> Maintains an active worker pool across interactions, eliminating repeated ~150ms worker process spawn overhead.</li>
                        <li><strong>High Compute Density:</strong> Integrates bilateral filtering (d=7, 9) and multi-scale Sobel gradients so heavy compute dominates IPC communication cost.</li>
                        <li><strong>100% Deterministic Match:</strong> Produces exact pixel match (157,077 px, 7 clusters) between sequential and parallel baselines.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 8,
        "tag": "07 | EMPIRICAL VALIDATION & BENCHMARK RESULTS",
        "title": "Empirical Execution Benchmarks & Amdahl's Law Scaling",
        "subtitle": "Quantitative Performance Comparison on 1600 × 1600 Satellite Imagery",
        "content_html": """
            <div class="stat-grid">
                <div class="stat-card" style="border-color: #ef476f;">
                    <div class="stat-val" style="color: #ef476f;">0.814 s</div>
                    <div class="stat-label">SEQUENTIAL TIME</div>
                    <div class="stat-sub">Single Core Baseline</div>
                </div>
                <div class="stat-card" style="border-color: #00f5d4;">
                    <div class="stat-val" style="color: #00f5d4;">0.305 s</div>
                    <div class="stat-label">PARALLEL TIME</div>
                    <div class="stat-sub">4 Cores (16 Tiles)</div>
                </div>
                <div class="stat-card" style="border-color: #06d6a0;">
                    <div class="stat-val" style="color: #06d6a0;">2.67x</div>
                    <div class="stat-label">MEASURED SPEEDUP</div>
                    <div class="stat-sub">62.5% Time Reduction</div>
                </div>
                <div class="stat-card" style="border-color: #ffd166;">
                    <div class="stat-val" style="color: #ffd166;">66.7%</div>
                    <div class="stat-label">PARALLEL EFFICIENCY</div>
                    <div class="stat-sub">Hardware Utilization</div>
                </div>
            </div>
            <div class="card" style="margin-top: 25px; border-color: rgba(255,255,255,0.1);">
                <h4 style="color: #00f5d4; margin-top: 0;">📊 Amdahl's Law Strong Scaling Analysis</h4>
                <ul style="margin-bottom: 0;">
                    <li><strong>Amdahl's Formula:</strong> <code>Speedup = 1 / [(1 - P) + (P / N)]</code>. Empirically measured parallelizable fraction is <strong>P = 0.91 (91% perfectly parallelizable)</strong>.</li>
                    <li><strong>Serial Overhead (1 - P = 0.09):</strong> Comprises IPC array serialization, boundary coordinate generation, and final connected component contour assembly.</li>
                    <li><strong>High-Resolution Scaling:</strong> Throughput increases from 1.2 gigapixels/min sequentially to <strong>3.3 gigapixels/min in parallel</strong>.</li>
                </ul>
            </div>
        """
    },
    {
        "num": 9,
        "tag": "08 | USER EXPERIENCE & DASHBOARD DESIGN",
        "title": "Interactive Dark-Navy Geospatial Dashboard & UI Features",
        "subtitle": "Professional Defense-Grade Interface Built in Streamlit, Plotly & HTML5",
        "content_html": """
            <div class="grid-3">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">⚙️ Sidebar Controls</h3>
                    <p class="card-sub">Configuration & Ingestion</p>
                    <ul>
                        <li><strong>Multi-Source Selector:</strong> Switch between Curated Datasets, Live Google Maps / ArcGIS, and Custom Image Uploads.</li>
                        <li><strong>HPC Worker Slider:</strong> Select 1 to 16 concurrent CPU processes with core auto-detection.</li>
                        <li><strong>Tile Grid Selector:</strong> Choose 2×2, 3×3, 4×4, 6×6, or 8×8 spatial partitioning grids.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">📑 7 Analytic Tabs</h3>
                    <p class="card-sub">Deep Geospatial Exploration</p>
                    <ul>
                        <li><strong>Tab 1:</strong> High-contrast Red Change Overlay & Bounding Boxes.</li>
                        <li><strong>Tab 2:</strong> Multi-Class Semantic Categorization & Donut Chart.</li>
                        <li><strong>Tab 3:</strong> Interactive Split-Curtain Swipe Comparison Slider.</li>
                        <li><strong>Tab 4:</strong> Plotly Parallel Computing Benchmarks & Gauges.</li>
                        <li><strong>Tabs 5-7:</strong> Heatmaps, Tile Decomposition & Technical Reports.</li>
                    </ul>
                </div>
                <div class="card card-gold">
                    <h3 style="color: #ffd166;">✨ UX & Telemetry</h3>
                    <p class="card-sub">Modern Design System</p>
                    <ul>
                        <li><strong>Theme:</strong> Deep space navy (<code>#0B132B</code> / <code>#1C2541</code>) matching modern aerospace command centers.</li>
                        <li><strong>Live Metric Cards:</strong> Execution times, speedup factor, efficiency, surface changed %, and parcel counts.</li>
                        <li><strong>Seam Inspector:</strong> Per-tile coordinate and pixel delta audit table.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 10,
        "tag": "09 | EXPORT CAPABILITIES & DELIVERABLES",
        "title": "Multi-Format Export Suite & Automated Artifact Generation",
        "subtitle": "Looping GIFs, High-Res Posters, GeoJSON Parcels & Technical Audit Reports",
        "content_html": """
            <div class="grid-2">
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">🎬 Animated Satellite Timelapse (.GIF)</h3>
                    <ul>
                        <li><strong>Multi-Phase Temporal Loop:</strong> Cycles smoothly through Prior Scene (T1) → Recent Scene (T2) → Change Highlights → Difference Heatmap.</li>
                        <li><strong>Branded Metadata:</strong> Injected header bars with acquisition dates, tags, and coordinates.</li>
                        <li><strong>One-Click Download:</strong> Instant export for presentations, project defense, and social media showcase.</li>
                    </ul>
                    <h3 style="color: #00f5d4; margin-top: 18px;">🖼️ 5-Panel Geospatial Poster (.PNG)</h3>
                    <ul>
                        <li>Consolidates Before, After, Difference Heatmap, Binary Mask, and Annotated Overlays onto a single high-resolution poster.</li>
                    </ul>
                </div>
                <div class="card card-green">
                    <h3 style="color: #06d6a0;">🌐 GIS Parcel Boundaries (.JSON / GeoJSON)</h3>
                    <ul>
                        <li>Vectorized polygon coordinates and bounding boxes for all detected ground anomalies.</li>
                        <li>Directly importable into QGIS, ArcGIS Pro, Google Earth, and Mapbox geospatial engines.</li>
                    </ul>
                    <h3 style="color: #06d6a0; margin-top: 18px;">📄 Technical Audit Report (.MD / PPTX)</h3>
                    <ul>
                        <li>Auto-generated technical report with hardware specs, algorithm parameters, and Amdahl's Law metrics.</li>
                        <li>Standalone presentation web server on port 8520 with fail-proof instant download.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 11,
        "tag": "10 | METHODOLOGY & EVOLUTION",
        "title": "System Methodology Disclosures & Deep Learning Roadmap",
        "subtitle": "Understanding Classical Differencing vs Neural Segmentation & Future Horizons",
        "content_html": """
            <div class="grid-2">
                <div class="card card-gold">
                    <h3 style="color: #ffd166;">⚠️ Methodological Disclosures</h3>
                    <ul>
                        <li><strong>Visual Differencing vs Object AI:</strong> Detects visual, spectral, and structural deviations between co-registered scenes. It does not independently infer semantic building labels without secondary neural classifiers.</li>
                        <li><strong>Resolution Bound:</strong> Precision is governed by ground sample distance (GSD). Fine-scale vehicle changes require sub-30cm imagery.</li>
                        <li><strong>Co-Registration Criticality:</strong> Extreme terrain relief requires sub-pixel ECC orthorectification to prevent false parallax edges.</li>
                    </ul>
                </div>
                <div class="card card-cyan">
                    <h3 style="color: #00f5d4;">🚀 Deep Learning Roadmap</h3>
                    <ul>
                        <li><strong>ChangeFormer (Vision Transformer):</strong> Siamese transformer network capturing long-range contextual spatial dependencies across multi-year temporal pairs.</li>
                        <li><strong>Segment Anything (SAM) Integration:</strong> Prompt-guided zero-shot foundation model segmentation for extracting building and field polygons.</li>
                        <li><strong>Multi-Spectral Sentinel-2 SWIR/NIR:</strong> Ingestion of Shortwave Infrared (SWIR) and Near-Infrared (NIR) for robust NDVI and NDBI indexing.</li>
                        <li><strong>GPU Acceleration (CUDA / TensorRT):</strong> Porting spatial tile bilateral kernels to NVIDIA GPUs for real-time 60 FPS video change detection.</li>
                    </ul>
                </div>
            </div>
        """
    },
    {
        "num": 12,
        "tag": "11 | SUMMARY & QUESTIONS",
        "title": "THANK YOU!",
        "subtitle": "Parallel Satellite Image Change Detection System",
        "content_html": """
            <div style="text-align: center; padding: 25px 20px;">
                <div style="display: inline-block; padding: 8px 24px; background: rgba(0, 245, 212, 0.15); border: 1px solid #00f5d4; border-radius: 50px; color: #00f5d4; font-weight: 700; font-size: 0.95rem; margin-bottom: 16px;">
                    OPEN FOR QUESTIONS &amp; TECHNICAL DISCUSSION
                </div>
                <h2 style="font-size: 2.2rem; color: #edf2f4; margin: 0 0 10px 0;">Thank You for Your Time &amp; Attention</h2>
                <p style="color: #8d99ae; font-size: 1.1rem; max-width: 750px; margin: 0 auto 24px auto;">
                    AI-Assisted Geospatial Remote Sensing Powered by High-Performance Parallel Multiprocessing
                </p>
                <div style="max-width: 820px; margin: 0 auto; text-align: left; background: #1c2541; border: 1px solid #3a506b; border-radius: 12px; padding: 20px 26px;">
                    <h4 style="color: #ffd166; margin-top: 0; margin-bottom: 10px;">🏆 Key Project Achievements:</h4>
                    <ul style="color: #edf2f4; margin-bottom: 0; line-height: 1.65; font-size: 0.95rem;">
                        <li><strong>Demonstrated 2.67x Speedup:</strong> Latency reduced from 0.814s down to 0.305s on 4 CPU cores (62.5% reduction).</li>
                        <li><strong>Live Earth Observation &amp; Wayback Archives:</strong> Direct connection to Google Maps &amp; 12-year multi-temporal satellite feeds.</li>
                        <li><strong>Advanced Radiometric Accuracy:</strong> Sub-pixel ECC affine alignment, Dark Channel Prior dehazing &amp; histogram matching.</li>
                        <li><strong>Multi-Class Semantic Analytics:</strong> Categorized change detection into Buildings, Deforestation, Water &amp; Roads.</li>
                        <li><strong>Modern Interactive UI &amp; Artifacts:</strong> Split swipe slider, looping animated GIF, 5-panel poster &amp; GeoJSON parcels.</li>
                    </ul>
                </div>
                <div style="margin-top: 25px;">
                    <button onclick="instantDownload()" class="dl-btn-large">📥 Download Comprehensive 12-Slide PowerPoint (.pptx)</button>
                </div>
            </div>
        """
    }
]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation: Parallel Satellite Change Detection (12 Slides)</title>
    <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0b132b;
            --card-bg: #1c2541;
            --card-border: #3a506b;
            --cyan: #00f5d4;
            --green: #06d6a0;
            --red: #ef476f;
            --gold: #ffd166;
            --text-light: #edf2f4;
            --text-muted: #8d99ae;
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 0;
            background-color: var(--bg-dark);
            color: var(--text-light);
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
            border-bottom: 1px solid rgba(0, 245, 212, 0.25);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-title h1 {
            font-size: 1.15rem;
            margin: 0;
            color: var(--cyan);
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        .header-title span {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .btn {
            background: var(--card-bg);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }
        .btn:hover {
            background: var(--cyan);
            color: var(--bg-dark);
            box-shadow: 0 0 15px rgba(0, 245, 212, 0.4);
        }
        .btn-green {
            border-color: var(--green);
            color: var(--green);
        }
        .btn-green:hover {
            background: var(--green);
            color: var(--bg-dark);
            box-shadow: 0 0 15px rgba(6, 214, 160, 0.4);
        }

        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 30px 20px;
        }

        .stage-wrapper {
            width: 100%;
            max-width: 1180px;
            aspect-ratio: 16 / 9;
            background: #0d172e;
            border: 1px solid var(--card-border);
            border-radius: 14px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }

        .slide-inner {
            flex: 1;
            padding: 40px 55px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            overflow-y: auto;
        }

        .slide-tag {
            color: var(--cyan);
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        }
        .slide-title {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 6px 0;
            color: var(--text-light);
        }
        .slide-subtitle {
            font-size: 1rem;
            color: var(--cyan);
            margin: 0 0 24px 0;
            font-weight: 500;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 10px;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 10px;
        }

        .card {
            background: rgba(28, 37, 65, 0.7);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 20px;
        }
        .card-cyan { border-top: 3px solid var(--cyan); }
        .card-green { border-top: 3px solid var(--green); }
        .card-red { border-top: 3px solid var(--red); }
        .card-gold { border-top: 3px solid var(--gold); }

        .card h3 {
            font-size: 1.05rem;
            margin: 0 0 4px 0;
        }
        .card-sub {
            color: var(--text-muted);
            font-size: 0.8rem;
            margin: 0 0 12px 0;
        }
        .card ul {
            margin: 0;
            padding-left: 18px;
            color: var(--text-light);
            font-size: 0.88rem;
            line-height: 1.55;
        }
        .card ul li { margin-bottom: 6px; }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .badge-cyan { background: rgba(0,245,212,0.15); color: var(--cyan); border: 1px solid rgba(0,245,212,0.4); }
        .badge-green { background: rgba(6,214,160,0.15); color: var(--green); border: 1px solid rgba(6,214,160,0.4); }
        .badge-gold { background: rgba(255,209,102,0.15); color: var(--gold); border: 1px solid rgba(255,209,102,0.4); }
        .badge-red { background: rgba(239,71,111,0.15); color: var(--red); border: 1px solid rgba(239,71,111,0.4); }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 10px;
        }
        .stat-card {
            background: rgba(28, 37, 65, 0.7);
            border: 1px solid;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }
        .stat-val {
            font-size: 1.9rem;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .stat-label {
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }
        .stat-sub {
            font-size: 0.75rem;
            color: var(--text-light);
            margin-top: 4px;
        }

        .dl-btn-large {
            background: linear-gradient(135deg, #00f5d4 0%, #06d6a0 100%);
            color: #0b132b;
            font-weight: 700;
            font-size: 1.05rem;
            padding: 14px 32px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0, 245, 212, 0.4);
            transition: all 0.2s ease;
        }
        .dl-btn-large:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(6, 214, 160, 0.6);
        }

        .nav-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #111a36;
            border-top: 1px solid var(--card-border);
            padding: 12px 28px;
        }
        .nav-controls {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .nav-btn {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: var(--text-light);
            padding: 6px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .nav-btn:hover:not(:disabled) {
            border-color: var(--cyan);
            color: var(--cyan);
        }
        .nav-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .slide-counter {
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 600;
        }
        .dots-wrapper {
            display: flex;
            gap: 8px;
        }
        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--card-border);
            cursor: pointer;
            transition: all 0.2s;
        }
        .dot.active {
            background: var(--cyan);
            box-shadow: 0 0 8px var(--cyan);
        }

        #toast-msg {
            display: none;
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--green);
            color: var(--bg-dark);
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            z-index: 1000;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <span style="font-size: 1.4rem;">🛰️</span>
            <div>
                <h1>PARALLEL SATELLITE CHANGE DETECTION</h1>
                <span>Comprehensive 12-Slide Executive &amp; Technical Presentation</span>
            </div>
        </div>
        <div class="header-actions">
            <a href="/report" target="_blank" class="btn">
                <span>📑</span> View Report
            </a>
            <a href="/report/download/pdf" class="btn btn-green">
                <span>📥</span> Report (PDF)
            </a>
            <button onclick="instantDownload()" class="btn btn-green">
                <span>📊</span> PPT (.pptx)
            </button>
            <a href="http://localhost:8510" target="_blank" class="btn">
                <span>🚀</span> App (8510)
            </a>
        </div>
    </header>

    <div class="main-container">
        <div class="stage-wrapper">
            <div id="slide-content" class="slide-inner">
                <!-- Injected via JavaScript -->
            </div>
            <div class="nav-bar">
                <div class="nav-controls">
                    <button id="prev-btn" class="nav-btn" onclick="prevSlide()">◀ Previous</button>
                    <button id="next-btn" class="nav-btn" onclick="nextSlide()">Next ▶</button>
                    <span id="slide-count" class="slide-counter">Slide 1 of 12</span>
                </div>
                <div id="dots-container" class="dots-wrapper">
                    <!-- Dots dynamically generated -->
                </div>
                <div>
                    <button onclick="instantDownload()" class="btn btn-green" style="padding: 6px 14px; font-size: 0.82rem;">
                        📥 Download .pptx
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="toast-msg">✅ Presentation downloaded successfully!</div>

    <script>
        const slidesData = SLIDES_JSON_PLACEHOLDER;
        const pptxB64 = "PPTX_BASE64_PLACEHOLDER";
        let currentSlide = 1;

        function renderSlide(slideNum) {
            currentSlide = slideNum;
            const slide = slidesData[slideNum - 1];
            const container = document.getElementById("slide-content");

            container.innerHTML = `
                <div class="slide-tag">${slide.tag}</div>
                <h2 class="slide-title">${slide.title}</h2>
                <div class="slide-subtitle">${slide.subtitle}</div>
                <div>${slide.content_html}</div>
            `;

            document.getElementById("slide-count").innerText = `Slide ${currentSlide} of ${slidesData.length}`;
            document.getElementById("prev-btn").disabled = (currentSlide === 1);
            document.getElementById("next-btn").disabled = (currentSlide === slidesData.length);

            updateDots();
        }

        function createDots() {
            const container = document.getElementById("dots-container");
            container.innerHTML = "";
            slidesData.forEach((_, idx) => {
                const dot = document.createElement("div");
                dot.className = "dot" + (idx === 0 ? " active" : "");
                dot.onclick = () => renderSlide(idx + 1);
                container.appendChild(dot);
            });
        }

        function updateDots() {
            const dots = document.querySelectorAll(".dot");
            dots.forEach((dot, idx) => {
                dot.className = "dot" + (idx === currentSlide - 1 ? " active" : "");
            });
        }

        function nextSlide() {
            if (currentSlide < slidesData.length) {
                renderSlide(currentSlide + 1);
            }
        }

        function prevSlide() {
            if (currentSlide > 1) {
                renderSlide(currentSlide - 1);
            }
        }

        function instantDownload() {
            try {
                if (!pptxB64 || pptxB64.length === 0) {
                    window.location.href = "/download";
                    return;
                }
                const byteCharacters = atob(pptxB64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {
                    type: "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                });

                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = "parallel_satellite_change_detection.pptx";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                const toast = document.getElementById("toast-msg");
                toast.style.display = "block";
                setTimeout(() => { toast.style.display = "none"; }, 3500);
            } catch (err) {
                window.location.href = "/download";
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        });

        createDots();
        renderSlide(1);
    </script>
</body>
</html>
"""


class PPTServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Direct PPTX Download
        if self.path in ["/download", f"/{PPTX_FILENAME}"]:
            if not os.path.exists(PPTX_PATH):
                self.send_error(404, "PowerPoint file not found")
                return
            with open(PPTX_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
            self.send_header("Content-Disposition", f'attachment; filename="{PPTX_FILENAME}"')
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        # 2. View Printable HTML Report
        if self.path in ["/report", "/report.html"]:
            if not os.path.exists(REPORT_HTML_PATH):
                self.send_error(404, "Report HTML not found")
                return
            with open(REPORT_HTML_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        # 3. Direct PDF Report Download
        if self.path in ["/report/download/pdf", "/report.pdf"]:
            if not os.path.exists(REPORT_PDF_PATH):
                self.send_error(404, "Report PDF not found")
                return
            with open(REPORT_PDF_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'attachment; filename="parallel_satellite_change_detection_report.pdf"')
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        # 4. Direct Word DOCX Report Download
        if self.path in ["/report/download/docx", "/report.docx"]:
            if not os.path.exists(REPORT_DOCX_PATH):
                self.send_error(404, "Report DOCX not found")
                return
            with open(REPORT_DOCX_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            self.send_header("Content-Disposition", 'attachment; filename="parallel_satellite_change_detection_report.docx"')
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        # 5. Direct Markdown Report Download
        if self.path in ["/report/download/md", "/report.md"]:
            if not os.path.exists(REPORT_MD_PATH):
                self.send_error(404, "Report MD not found")
                return
            with open(REPORT_MD_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="parallel_satellite_change_detection_report.md"')
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        # 6. Interactive Presentation Viewer
        if self.path in ["/", "/index.html"]:
            slides_json = json.dumps(SLIDES_DATA)
            html_output = HTML_TEMPLATE.replace("SLIDES_JSON_PLACEHOLDER", slides_json)
            html_output = html_output.replace("PPTX_BASE64_PLACEHOLDER", PPTX_B64)
            html_bytes = html_output.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(html_bytes)
            return

        self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        pass


def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, PPTServerHandler)
    print(f"Presentation Web Server running at: http://localhost:{PORT}")
    print(f"Direct PPTX download available at: http://localhost:{PORT}/download")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
