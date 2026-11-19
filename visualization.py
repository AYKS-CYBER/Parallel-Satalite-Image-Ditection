"""
visualization.py
================
Visualizations and interactive charts for the Satellite Change Detection System.
Includes dark-themed Plotly charts and high-resolution composite image generation.
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import cv2
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List, Optional, Tuple


# Dark dashboard color scheme
COLOR_NAVY_DARK = "#0b132b"
COLOR_NAVY_CARD = "#1c2541"
COLOR_CYAN_ACCENT = "#00f5d4"
COLOR_GREEN_ACCENT = "#06d6a0"
COLOR_RED_ACCENT = "#ef476f"
COLOR_GOLD_ACCENT = "#ffd166"
COLOR_TEXT_MUTED = "#8d99ae"
COLOR_TEXT_LIGHT = "#edf2f4"


def create_execution_comparison_chart(
    seq_time: float,
    par_time: float,
    num_processes: int,
    tile_count: int
) -> go.Figure:
    """
    Creates an interactive Plotly bar chart comparing Sequential vs Parallel runtime.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Sequential Processing<br>(Single Core)", f"Parallel Processing<br>({num_processes} CPU Workers)"],
        y=[seq_time, par_time],
        marker=dict(
            color=[COLOR_RED_ACCENT, COLOR_CYAN_ACCENT],
            line=dict(color="#ffffff", width=1.5)
        ),
        text=[f"{seq_time:.3f} s", f"{par_time:.3f} s"],
        textposition="outside",
        textfont=dict(size=14, color=COLOR_TEXT_LIGHT, family="Arial Black"),
        width=0.45
    ))

    speedup = seq_time / par_time if par_time > 0 else 1.0
    time_saved = max(0.0, seq_time - par_time)
    pct_reduction = (time_saved / seq_time) * 100.0 if seq_time > 0 else 0.0

    title_text = (
        f"<b>Execution Time Comparison</b> &nbsp;|&nbsp; "
        f"<span style='color:{COLOR_GREEN_ACCENT}; font-size:15px;'>"
        f"Speedup: {speedup:.2f}x &nbsp;({pct_reduction:.1f}% time reduction with {tile_count} tiles)</span>"
    )

    fig.update_layout(
        title=dict(text=title_text, font=dict(color=COLOR_TEXT_LIGHT, size=16)),
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=55, b=40),
        yaxis=dict(
            title=dict(text="Execution Time (Seconds)", font=dict(color=COLOR_TEXT_MUTED, size=13)),
            tickfont=dict(color=COLOR_TEXT_LIGHT),
            gridcolor="rgba(255, 255, 255, 0.08)",
            zerolinecolor="rgba(255, 255, 255, 0.2)"
        ),
        xaxis=dict(
            tickfont=dict(color=COLOR_TEXT_LIGHT, size=13)
        ),
        showlegend=False,
        height=340
    )

    return fig


def create_speedup_efficiency_gauges(
    speedup: float,
    efficiency: float,
    num_processes: int
) -> go.Figure:
    """
    Creates side-by-side indicator gauges for Speedup Factor and Parallel Efficiency %.
    """
    fig = go.Figure()

    # Gauge 1: Speedup
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=speedup,
        number=dict(suffix="x", font=dict(color=COLOR_CYAN_ACCENT, size=32)),
        title=dict(
            text=f"<b>Compute Speedup</b><br><span style='font-size:12px; color:{COLOR_TEXT_MUTED}'>Ideal: {num_processes:.1f}x</span>",
            font=dict(color=COLOR_TEXT_LIGHT, size=14)
        ),
        gauge=dict(
            axis=dict(range=[0, max(num_processes, 4)], tickcolor=COLOR_TEXT_LIGHT),
            bar=dict(color=COLOR_CYAN_ACCENT),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=1,
            bordercolor="rgba(255,255,255,0.15)",
            steps=[
                dict(range=[0, num_processes * 0.4], color="rgba(239, 71, 111, 0.2)"),
                dict(range=[num_processes * 0.4, num_processes * 0.75], color="rgba(255, 209, 102, 0.2)"),
                dict(range=[num_processes * 0.75, num_processes], color="rgba(6, 214, 160, 0.2)")
            ]
        ),
        domain=dict(x=[0.0, 0.46], y=[0, 1])
    ))

    # Gauge 2: Efficiency
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=min(100.0, efficiency),
        number=dict(suffix="%", font=dict(color=COLOR_GREEN_ACCENT, size=32)),
        title=dict(
            text=f"<b>Parallel Efficiency</b><br><span style='font-size:12px; color:{COLOR_TEXT_MUTED}'>Speedup / {num_processes} Cores</span>",
            font=dict(color=COLOR_TEXT_LIGHT, size=14)
        ),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=COLOR_TEXT_LIGHT),
            bar=dict(color=COLOR_GREEN_ACCENT),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=1,
            bordercolor="rgba(255,255,255,0.15)",
            steps=[
                dict(range=[0, 40], color="rgba(239, 71, 111, 0.2)"),
                dict(range=[40, 70], color="rgba(255, 209, 102, 0.2)"),
                dict(range=[70, 100], color="rgba(6, 214, 160, 0.2)")
            ]
        ),
        domain=dict(x=[0.54, 1.0], y=[0, 1])
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        height=220
    )

    return fig


def create_surface_change_donut(total_pixels: int, changed_pixels: int) -> go.Figure:
    """
    Creates a donut chart displaying changed surface area percentage vs unchanged.
    """
    unchanged = max(0, total_pixels - changed_pixels)
    pct = (changed_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

    fig = go.Figure(data=[go.Pie(
        labels=["Changed Surface", "Unchanged Surface"],
        values=[changed_pixels, unchanged],
        hole=0.68,
        marker=dict(colors=[COLOR_RED_ACCENT, "rgba(58, 80, 107, 0.5)"]),
        textinfo="percent",
        textfont=dict(color=COLOR_TEXT_LIGHT, size=13),
        hoverinfo="label+value+percent"
    )])

    fig.update_layout(
        title=dict(text=f"<b>Land Cover Change Ratio</b> ({pct:.2f}%)", font=dict(color=COLOR_TEXT_LIGHT, size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        showlegend=True,
        legend=dict(font=dict(color=COLOR_TEXT_LIGHT, size=11), orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=240,
        annotations=[dict(text=f"<b>{pct:.1f}%</b><br><span style='font-size:10px; color:{COLOR_TEXT_MUTED}'>Changed</span>",
                          x=0.5, y=0.5, font_size=16, font_color=COLOR_CYAN_ACCENT, showarrow=False)]
    )

    return fig


def create_scaling_comparison_chart(scaling_records: List[Dict[str, Any]]) -> go.Figure:
    """
    Plots multi-worker strong scaling curve: Measured Speedup vs Theoretical Linear Speedup.
    """
    cores = [r["cores"] for r in scaling_records]
    speedups = [r["speedup"] for r in scaling_records]

    fig = go.Figure()

    # Ideal linear speedup
    fig.add_trace(go.Scatter(
        x=cores,
        y=cores,
        mode="lines",
        name="Ideal Linear Speedup",
        line=dict(color="rgba(255, 255, 255, 0.4)", dash="dash", width=2)
    ))

    # Measured Speedup
    fig.add_trace(go.Scatter(
        x=cores,
        y=speedups,
        mode="lines+markers",
        name="Measured Speedup",
        line=dict(color=COLOR_CYAN_ACCENT, width=3),
        marker=dict(size=8, color=COLOR_GREEN_ACCENT, line=dict(color="#ffffff", width=1.5))
    ))

    fig.update_layout(
        title=dict(text="<b>Multiprocessing Scaling Curve (Amdahl's Law)</b>", font=dict(color=COLOR_TEXT_LIGHT, size=15)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        margin=dict(l=40, r=30, t=45, b=40),
        xaxis=dict(
            title=dict(text="CPU Worker Processes", font=dict(color=COLOR_TEXT_MUTED)),
            tickfont=dict(color=COLOR_TEXT_LIGHT),
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title=dict(text="Speedup Factor", font=dict(color=COLOR_TEXT_MUTED)),
            tickfont=dict(color=COLOR_TEXT_LIGHT),
            gridcolor="rgba(255,255,255,0.08)"
        ),
        legend=dict(font=dict(color=COLOR_TEXT_LIGHT), x=0.02, y=0.98),
        height=320
    )

    return fig


def generate_composite_report_image(
    before_img: np.ndarray,
    after_img: np.ndarray,
    diff_heatmap: np.ndarray,
    binary_mask: np.ndarray,
    overlay_img: np.ndarray,
    metrics: Dict[str, Any],
    speedup: float,
    efficiency: float,
    seq_time: float,
    par_time: float,
    num_processes: int
) -> np.ndarray:
    """
    Creates a single consolidated high-resolution 5-panel geospatial analysis poster
    ready for download, including headers, metrics cards, and side-by-side satellite imagery.
    """
    # Downscale panels to standard size for poster
    panel_w, panel_h = 420, 420

    def prepare_panel(img, is_gray=False):
        if is_gray:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        return cv2.resize(img, (panel_w, panel_h), interpolation=cv2.INTER_AREA)

    p1 = prepare_panel(before_img)
    p2 = prepare_panel(after_img)
    p3 = prepare_panel(diff_heatmap)
    p4 = prepare_panel(binary_mask, is_gray=True)
    p5 = prepare_panel(overlay_img)

    # Poster dimensions: 3 columns, 2 rows of imagery + header & footer
    # Layout:
    # Row 1: [Before Satellite] [After Satellite] [Diff Heatmap]
    # Row 2: [Binary Mask]      [Annotated Changes Overlay] [Summary Metrics Panel]
    canvas_w = panel_w * 3 + 80
    canvas_h = 160 + panel_h * 2 + 100
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    # Background navy color
    canvas[:] = (11, 19, 43)

    # Header section
    cv2.putText(canvas, "SATELLITE CHANGE DETECTION SYSTEM", (30, 50),
                cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 245, 212), 2, cv2.LINE_AA)
    cv2.putText(canvas, "PARALLEL COMPUTING GEOSPATIAL ANALYSIS REPORT", (30, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (141, 153, 174), 1, cv2.LINE_AA)
    cv2.line(canvas, (30, 110), (canvas_w - 30, 110), (58, 80, 107), 1)

    # Coordinates for panels
    # Row 1
    y_r1 = 140
    canvas[y_r1:y_r1 + panel_h, 25:25 + panel_w] = p1
    cv2.putText(canvas, "1. BEFORE SATELLITE IMAGE", (30, y_r1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (237, 242, 244), 1, cv2.LINE_AA)

    canvas[y_r1:y_r1 + panel_h, 45 + panel_w:45 + panel_w * 2] = p2
    cv2.putText(canvas, "2. AFTER SATELLITE IMAGE", (50 + panel_w, y_r1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (237, 242, 244), 1, cv2.LINE_AA)

    canvas[y_r1:y_r1 + panel_h, 65 + panel_w * 2:65 + panel_w * 3] = p3
    cv2.putText(canvas, "3. RADIOMETRIC DIFFERENCE HEATMAP", (70 + panel_w * 2, y_r1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (237, 242, 244), 1, cv2.LINE_AA)

    # Row 2
    y_r2 = y_r1 + panel_h + 45
    canvas[y_r2:y_r2 + panel_h, 25:25 + panel_w] = p4
    cv2.putText(canvas, "4. BINARY CHANGE MASK (CLEANED)", (30, y_r2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (237, 242, 244), 1, cv2.LINE_AA)

    canvas[y_r2:y_r2 + panel_h, 45 + panel_w:45 + panel_w * 2] = p5
    cv2.putText(canvas, "5. DETECTED CHANGES OVERLAY", (50 + panel_w, y_r2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (237, 242, 244), 1, cv2.LINE_AA)

    # Panel 6: Metrics Card
    m_x = 65 + panel_w * 2
    cv2.rectangle(canvas, (m_x, y_r2), (m_x + panel_w, y_r2 + panel_h), (28, 37, 65), -1)
    cv2.rectangle(canvas, (m_x, y_r2), (m_x + panel_w, y_r2 + panel_h), (0, 245, 212), 1)

    cv2.putText(canvas, "SYSTEM PERFORMANCE SUMMARY", (m_x + 20, y_r2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 245, 212), 1, cv2.LINE_AA)
    cv2.line(canvas, (m_x + 20, y_r2 + 48), (m_x + panel_w - 20, y_r2 + 48), (58, 80, 107), 1)

    lines = [
        f"Sequential Time: {seq_time:.3f} s",
        f"Parallel Time:   {par_time:.3f} s",
        f"Speedup Factor:  {speedup:.2f}x",
        f"Parallel Efficiency: {efficiency:.1f}%",
        f"CPU Worker Cores:    {num_processes}",
        "",
        "GEOSPATIAL DETECTION STATS",
        f"Surface Changed: {metrics.get('change_percentage', 0.0):.2f}%",
        f"Changed Pixels:  {metrics.get('changed_pixels', 0):,}",
        f"Changed Regions: {metrics.get('region_count', 0):,} clusters",
        f"Resolution:      {before_img.shape[1]}x{before_img.shape[0]} px"
    ]

    curr_y = y_r2 + 80
    for line in lines:
        if line == "GEOSPATIAL DETECTION STATS":
            cv2.line(canvas, (m_x + 20, curr_y - 12), (m_x + panel_w - 20, curr_y - 12), (58, 80, 107), 1)
            cv2.putText(canvas, line, (m_x + 20, curr_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (6, 214, 160), 1, cv2.LINE_AA)
            curr_y += 28
        elif line == "":
            curr_y += 10
        else:
            cv2.putText(canvas, line, (m_x + 20, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (237, 242, 244), 1, cv2.LINE_AA)
            curr_y += 26

    # Footer
    cv2.line(canvas, (30, canvas_h - 45), (canvas_w - 30, canvas_h - 45), (58, 80, 107), 1)
    footer_text = "Generated by Satellite Change Detection System - High Performance Geospatial Multiprocessing"
    cv2.putText(canvas, footer_text, (30, canvas_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (141, 153, 174), 1, cv2.LINE_AA)

    return canvas


def create_semantic_breakdown_pie(percentages: Dict[str, float]) -> go.Figure:
    """
    Creates an interactive Plotly donut chart displaying the distribution of detected changes:
    - New Construction (Red)
    - Vegetation Loss (Green)
    - Water Surface Dynamics (Blue)
    - Road / Soil Infrastructure (Gold)
    """
    labels = list(percentages.keys())
    values = [max(0.01, percentages[k]) for k in labels]

    color_map = {
        "New Construction": "#ef476f",
        "Vegetation Loss": "#06d6a0",
        "Water Surface Dynamics": "#118ab2",
        "Road / Soil Infrastructure": "#ffd166"
    }
    colors = [color_map.get(k, "#00f5d4") for k in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0b132b", width=2)),
        textinfo="label+percent",
        textfont=dict(color=COLOR_TEXT_LIGHT, size=12),
        hoverinfo="label+percent"
    )])

    fig.update_layout(
        title=dict(text="<b>Multi-Class Semantic Change Distribution</b>", font=dict(color=COLOR_TEXT_LIGHT, size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        showlegend=True,
        legend=dict(font=dict(color=COLOR_TEXT_LIGHT, size=11), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=280
    )
    return fig


def create_interactive_swipe_html(before_img: np.ndarray, after_img: np.ndarray) -> str:
    """
    Builds an interactive split-view comparison slider HTML component
    allowing the user to drag a curtain across the Before vs After satellite scenes.
    """
    import base64
    from PIL import Image
    import io

    def to_b64(img_arr):
        # Resize to max 900px wide for snappy rendering
        h, w = img_arr.shape[:2]
        if w > 900:
            scale = 900.0 / w
            img_arr = cv2.resize(img_arr, (900, int(h * scale)), interpolation=cv2.INTER_AREA)
        pil_im = Image.fromarray(img_arr)
        buf = io.BytesIO()
        pil_im.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    b64_before = to_b64(before_img)
    b64_after = to_b64(after_img)

    html = f"""
    <div style="width: 100%; max-width: 900px; margin: 0 auto; font-family: sans-serif;">
        <div style="position: relative; width: 100%; aspect-ratio: 16/9; overflow: hidden; border-radius: 12px; border: 1px solid rgba(0, 245, 212, 0.4); box-shadow: 0 8px 30px rgba(0,0,0,0.5);" id="swipe-container">
            <!-- Background Image: Time T2 After -->
            <img src="data:image/jpeg;base64,{b64_after}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; user-select: none;">
            <div style="position: absolute; top: 12px; right: 14px; background: rgba(11, 19, 43, 0.75); color: #00f5d4; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 4px; pointer-events: none; border: 1px solid #00f5d4;">
                TIME T2 (CURRENT OBSERVATION)
            </div>

            <!-- Foreground Image: Time T1 Before (Clipped by slider) -->
            <div id="swipe-clip" style="position: absolute; top: 0; left: 0; width: 50%; height: 100%; overflow: hidden; border-right: 3px solid #00f5d4;">
                <img src="data:image/jpeg;base64,{b64_before}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; user-select: none; max-width: none;" id="swipe-before-img">
                <div style="position: absolute; top: 12px; left: 14px; background: rgba(11, 19, 43, 0.75); color: #ffd166; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 4px; pointer-events: none; border: 1px solid #ffd166;">
                    TIME T1 (HISTORICAL BASELINE)
                </div>
            </div>

            <!-- Draggable Range Input -->
            <input type="range" min="0" max="100" value="50" id="swipe-slider" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: ew-resize; margin: 0; z-index: 10;" oninput="updateSwipe(this.value)">

            <!-- Center Divider Handle Icon -->
            <div id="swipe-handle" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 36px; height: 36px; background: #00f5d4; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(0, 245, 212, 0.6); pointer-events: none; color: #0b132b; font-weight: bold; font-size: 14px;">
                ◀▶
            </div>
        </div>
        <p style="text-align: center; color: #8d99ae; font-size: 12px; margin-top: 8px;">
            ↔️ Click and drag the divider left or right to swipe between Historical T1 and Current T2 satellite imagery
        </p>
    </div>

    <script>
        function updateSwipe(val) {{
            const clip = document.getElementById('swipe-clip');
            const handle = document.getElementById('swipe-handle');
            const beforeImg = document.getElementById('swipe-before-img');
            const container = document.getElementById('swipe-container');

            clip.style.width = val + '%';
            handle.style.left = val + '%';
            // Maintain 100% width relative to container
            beforeImg.style.width = container.offsetWidth + 'px';
        }}
        window.addEventListener('resize', () => {{
            const container = document.getElementById('swipe-container');
            const beforeImg = document.getElementById('swipe-before-img');
            if (container && beforeImg) beforeImg.style.width = container.offsetWidth + 'px';
        }});
        setTimeout(() => {{
            const container = document.getElementById('swipe-container');
            const beforeImg = document.getElementById('swipe-before-img');
            if (container && beforeImg) beforeImg.style.width = container.offsetWidth + 'px';
        }}, 100);
    </script>
    """
    return html
