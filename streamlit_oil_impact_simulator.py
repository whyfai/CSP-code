from __future__ import annotations

from html import escape
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components

from impact_model import calculate_impacts

BAR_COLORS = ["#3366cc", "#dc3912", "#ff9900", "#109618"]
APP_BG = "#f3efe6"
CARD_BG = "#fbf9f4"
TITLE_COLOR = "#1f2a37"
TEXT_COLOR = "#2c3e50"
MUTED_TEXT = "#566573"
ACCENT = "#c27d28"
BASELINE_CRUDE_PRICE = 50.0
MIN_CRUDE_PRICE = 30.0
MAX_CRUDE_PRICE = 200.0
DEPENDENT_LABELS = ["Transportation", "Food Cost", "Annual Expenditure", "Healthcare"]
VALUE_UNIT = "CPI"


def money(value: float) -> str:
    return f"${value:,.2f}"


def percent_change(current_value: float, baseline_value: float) -> float:
    if baseline_value == 0:
        return 0.0
    return ((current_value - baseline_value) / baseline_value) * 100


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def build_comparison_card(impacts: dict[str, float]) -> str:
    labels = ["Crude Oil", *DEPENDENT_LABELS]
    values = [impacts[label] for label in labels]
    max_value = max(values) if values else 1

    rows = []
    for label, value, color in zip(labels, values, ["#1d4ed8", *BAR_COLORS], strict=True):
        width = 8 if max_value == 0 else max(8, (value / max_value) * 100)
        rows.append(
            f"""
            <div class="bar-row">
                <div class="bar-label">{escape(label)}</div>
                <div class="bar-track"><div class="bar-fill" style="width:{width:.2f}%;background:{color};"></div></div>
                <div class="bar-value">{escape(money(value))}</div>
            </div>
            """
        )

    return dedent(
        """
        <div class="card-shell">
            <div class="chart-title">Live cost comparison</div>
            <div class="chart-subtitle">Relative impact scales with the crude oil input above.</div>
            {rows}
        </div>
        """
    ).format(rows="\n".join(rows))


def build_svg_trend_graph() -> str:
    x_values = list(range(30, 201, 10))
    baseline_impacts = calculate_impacts(BASELINE_CRUDE_PRICE)
    trend_data = {
        label: [calculate_impacts(float(price))[label] for price in x_values]
        for label in DEPENDENT_LABELS
    }
    percent_change_data = {
        label: [percent_change(value, baseline_impacts[label]) for value in series]
        for label, series in trend_data.items()
    }

    chart_left, chart_top = 68, 34
    chart_width, chart_height = 730, 380
    chart_right = chart_left + chart_width
    chart_bottom = chart_top + chart_height

    y_values = [value for series in percent_change_data.values() for value in series]
    y_min = min(y_values)
    y_max = max(y_values)
    if y_min == y_max:
        y_max = y_min + 1

    def map_x(price: float) -> float:
        return chart_left + ((price - x_values[0]) / (x_values[-1] - x_values[0])) * chart_width

    def map_y(value: float) -> float:
        return chart_bottom - ((value - y_min) / (y_max - y_min)) * chart_height

    parts = [
        '<svg viewBox="0 0 900 520" role="img" aria-label="Dependent variable trends by crude oil price" width="100%" height="520" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="900" height="520" rx="24" fill="#fffef9"/>',
        f'<text x="{chart_left}" y="18" fill="{TITLE_COLOR}" font-family="Segoe UI, sans-serif" font-size="16" font-weight="700">Dependent variable trends by crude oil price</text>',
        f'<text x="{chart_left}" y="34" fill="{MUTED_TEXT}" font-family="Segoe UI, sans-serif" font-size="10">X axis: crude oil ($/barrel)   |   Y axis: percent change from $50 baseline</text>',
    ]

    for i in range(6):
        y = chart_top + (i * chart_height / 5)
        parts.append(f'<line x1="{chart_left}" y1="{y:.2f}" x2="{chart_right}" y2="{y:.2f}" stroke="#e9e2d4" stroke-width="1"/>')

    for i in range(6):
        x = chart_left + (i * chart_width / 5)
        parts.append(f'<line x1="{x:.2f}" y1="{chart_top}" x2="{x:.2f}" y2="{chart_bottom}" stroke="#f2ebe0" stroke-width="1"/>')

    zero_y = map_y(0)
    parts.append(f'<line x1="{chart_left}" y1="{zero_y:.2f}" x2="{chart_right}" y2="{zero_y:.2f}" stroke="#94a3b8" stroke-width="2"/>')
    parts.append(f'<line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_bottom}" stroke="#b7ad97" stroke-width="2"/>')
    parts.append(f'<line x1="{chart_left}" y1="{chart_bottom}" x2="{chart_right}" y2="{chart_bottom}" stroke="#b7ad97" stroke-width="2"/>')

    for price in x_values[::2]:
        x = map_x(float(price))
        parts.append(
            f'<text x="{x:.2f}" y="{chart_bottom + 16}" fill="{MUTED_TEXT}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="8">${price}</text>'
        )

    y_ticks = 5
    for i in range(y_ticks + 1):
        value = y_min + (i * (y_max - y_min) / y_ticks)
        y = map_y(value)
        parts.append(
            f'<text x="{chart_left - 8}" y="{y + 3:.2f}" fill="{MUTED_TEXT}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="8">{value:+.0f}%</text>'
        )

    for index, label in enumerate(DEPENDENT_LABELS):
        points = []
        for price, value in zip(x_values, percent_change_data[label], strict=True):
            points.append(f"{map_x(float(price)):.2f},{map_y(value):.2f}")
        color = BAR_COLORS[index]
        points_str = " ".join(points)
        parts.append(
            f'<polyline points="{points_str}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        last_x, last_y = points[-1].split(",")
        parts.append(f'<circle cx="{float(last_x):.2f}" cy="{float(last_y):.2f}" r="4" fill="{color}"/>')

    legend_x = chart_right - 190
    legend_y = chart_top + 16
    parts.append(
        f'<rect x="{legend_x - 12}" y="{legend_y - 12}" width="190" height="100" rx="12" fill="#fffdf8" stroke="#e6dcc7"/>'
    )
    for index, label in enumerate(DEPENDENT_LABELS):
        y = legend_y + (index * 20)
        color = BAR_COLORS[index]
        parts.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 22}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        parts.append(
            f'<text x="{legend_x + 28}" y="{y + 3}" fill="{TEXT_COLOR}" font-family="Segoe UI, sans-serif" font-size="8" font-weight="700">{escape(label)}</text>'
        )

    parts.append(
        f'<text x="{chart_left}" y="{chart_bottom + 34}" fill="{MUTED_TEXT}" font-family="Segoe UI, sans-serif" font-size="8">Each line shows its own percent change from the $50 baseline so the curves are directly comparable.</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def render_metric(label: str, value: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sync_price_from_slider() -> None:
    price = float(st.session_state.crude_price_slider)
    st.session_state.crude_price_entry = f"{price:.2f}"


def apply_manual_price() -> None:
    raw_value = str(st.session_state.crude_price_entry).strip()
    try:
        price = float(raw_value)
    except ValueError:
        st.session_state.crude_price_entry = f"{st.session_state.crude_price_slider:.2f}"
        return

    price = clamp(price, MIN_CRUDE_PRICE, MAX_CRUDE_PRICE)
    st.session_state.crude_price_slider = price
    st.session_state.crude_price_entry = f"{price:.2f}"


st.set_page_config(page_title="Crude Oil Price Impact Simulator", layout="wide")

if "crude_price_slider" not in st.session_state:
    st.session_state.crude_price_slider = 80.0
if "crude_price_entry" not in st.session_state:
    st.session_state.crude_price_entry = "80.0"

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f3efe6 0%, #f9f7f1 100%);
            color: #1f2a37;
            font-family: "Segoe UI", system-ui, sans-serif;
        }

        .hero {
            border: 1px solid rgba(31, 41, 55, 0.10);
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.72);
            padding: 24px 24px 20px;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
            margin-bottom: 16px;
        }

        .eyebrow {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(194, 125, 40, 0.12);
            color: #9a5f15;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .hero h1 {
            margin: 0;
            color: #1f2a37;
            font-size: clamp(2rem, 4vw, 3.1rem);
            line-height: 1.05;
        }

        .hero p {
            margin-top: 12px;
            max-width: 920px;
            color: #566573;
            font-size: 1.02rem;
            line-height: 1.55;
        }

        .controls-card, .section-card, .metric-card, .card-shell {
            border: 1px solid rgba(31, 41, 55, 0.10);
            background: rgba(251, 249, 244, 0.95);
            border-radius: 22px;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        }

        .controls-card {
            padding: 18px 18px 14px;
            margin-bottom: 16px;
        }

        .section-card {
            padding: 18px;
        }

        .chart-title {
            color: #2c3e50;
            font-size: 1.05rem;
            font-weight: 800;
        }

        .chart-subtitle {
            margin-top: 4px;
            margin-bottom: 14px;
            color: #566573;
            font-size: 0.92rem;
        }

        .metric-card {
            padding: 16px 16px 14px;
        }

        .metric-label {
            color: #566573;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-value {
            margin-top: 6px;
            color: #c27d28;
            font-size: 1.75rem;
            font-weight: 800;
        }

        .metric-caption {
            margin-top: 6px;
            color: #566573;
            font-size: 0.88rem;
            line-height: 1.4;
        }

        .bar-row {
            display: grid;
            grid-template-columns: 140px 1fr 92px;
            gap: 12px;
            align-items: center;
            margin: 12px 0;
        }

        .bar-label {
            color: #2c3e50;
            font-size: 0.95rem;
            font-weight: 700;
        }

        .bar-track {
            height: 14px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.18);
            overflow: hidden;
            position: relative;
        }

        .bar-fill {
            height: 100%;
            border-radius: 999px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.14);
        }

        .bar-value {
            text-align: right;
            color: #1f2a37;
            font-size: 0.95rem;
            font-weight: 800;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 0.15rem;
            padding-bottom: 0.5rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.45rem 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Streamlit edition</div>
        <h1>Crude Oil Impact Simulator</h1>
        <p>
            Move the crude oil price and watch transportation, food cost, annual expenditure,
            and healthcare update from the same model used by the desktop app.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="controls-card">
        <div class="chart-title">Controls</div>
        <div class="chart-subtitle">Adjust the crude oil price with the slider or enter a value directly.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

control_left, control_right = st.columns([4, 1], gap="large")
with control_left:
    st.slider(
        "Crude oil price ($/barrel)",
        min_value=MIN_CRUDE_PRICE,
        max_value=MAX_CRUDE_PRICE,
        step=0.5,
        key="crude_price_slider",
        on_change=sync_price_from_slider,
    )
with control_right:
    st.text_input("Or type a price", key="crude_price_entry")
    st.button("Apply", use_container_width=True, on_click=apply_manual_price)

st.caption("Tip: dependent values are shown in CPI units. Percent change compares against a $50-per-barrel baseline.")

current_price = round(float(st.session_state.crude_price_slider), 2)
impacts = calculate_impacts(current_price)
baseline_impacts = calculate_impacts(BASELINE_CRUDE_PRICE)

summary_tab, trend_tab = st.tabs(["Summary", "Trend Graph"])

with summary_tab:
    st.markdown(
        """
        <div class="section-card" style="margin-bottom:16px;">
            <div class="chart-title">Current model outputs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4, gap="medium")
    for column, name in zip(metric_cols, DEPENDENT_LABELS, strict=True):
        current_value = impacts[name]
        percent = percent_change(current_value, baseline_impacts[name])
        with column:
            render_metric(
                name,
                f"{current_value:,.2f} {VALUE_UNIT}",
                f"{percent:+.1f}% vs ${BASELINE_CRUDE_PRICE:.0f}/barrel",
            )

    st.markdown(build_comparison_card(impacts), unsafe_allow_html=True)

with trend_tab:
    st.markdown(
        """
        <div class="section-card" style="margin-bottom:16px;">
            <div class="chart-title">Trend Graph</div>
            <div class="chart-subtitle">Each line shows percent change from the $50 baseline across the tested price range.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components.html(build_svg_trend_graph(), height=540, scrolling=False)

    st.markdown(
        """
        <div class="section-card">
            <div class="chart-title">Interpretation</div>
            <div class="chart-subtitle">These are simplified illustrative estimates, not market forecasts.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )