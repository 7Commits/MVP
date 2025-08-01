import streamlit as st


def create_card(title: str, content: str, icon: str | None = None,
                is_success: bool = False, is_warning: bool = False, is_error: bool = False):
    """Crea una scheda stilizzata con un contenuto personalizzabile."""
    color = "#4F6AF0"
    bg_color = "white"
    shadow_color = "rgba(79, 106, 240, 0.15)"

    if is_success:
        color = "#28a745"
        bg_color = "#f8fff9"
        shadow_color = "rgba(40, 167, 69, 0.15)"
    elif is_warning:
        color = "#ffc107"
        bg_color = "#fffef8"
        shadow_color = "rgba(255, 193, 7, 0.15)"
    elif is_error:
        color = "#dc3545"
        bg_color = "#fff8f8"
        shadow_color = "rgba(220, 53, 69, 0.15)"

    icon_text = f'<span class="card-icon">{icon}</span>' if icon else ""

    st.markdown(
        f"""
    <style>
        .custom-card {{
            border-radius: 12px;
            border: 1px solid rgba({color.replace('#', '')}, 0.3);
            border-left: 5px solid {color};
            padding: 1.25rem;
            background-color: {bg_color};
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 15px {shadow_color};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .custom-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px {shadow_color};
        }}
        .card-title {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            color: {color};
            display: flex;
            align-items: center;
        }}
        .card-content {{
            color: #333;
            line-height: 1.6;
        }}
        .card-icon {{
            font-size: 1.3rem;
            margin-right: 0.5rem;
        }}
    </style>

    <div class="custom-card">
        <div class="card-title">{icon_text}{title}</div>
        <div class="card-content">{content}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_metrics_container(metrics_data: list[dict]):
    """Crea un contenitore con metriche ben stilizzate."""
    st.markdown(
        """
    <style>
        .metrics-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1.25rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            flex: 1;
            min-width: 160px;
            background: white;
            border-radius: 12px;
            padding: 1.5rem 1rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border: 1px solid rgba(230, 235, 255, 0.9);
            position: relative;
            overflow: hidden;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(79, 106, 240, 0.15);
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #4F6AF0, #7D8EF7);
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: bold;
            color: #4F6AF0;
            margin: 0.5rem 0;
            text-shadow: 0 2px 10px rgba(79, 106, 240, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .metric-unit {
            font-size: 1.2rem;
            margin-left: 0.25rem;
            opacity: 0.8;
        }
        .metric-label {
            font-size: 1rem;
            color: #555;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        .metric-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #F0F4FF, #E6EBFF);
            width: 60px;
            height: 60px;
            line-height: 60px;
            border-radius: 50%;
            margin: 0 auto 1rem auto;
            box-shadow: 0 4px 15px rgba(79, 106, 240, 0.1);
        }

        @keyframes metric-appear {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .metric-card {
            animation: metric-appear 0.6s ease forwards;
        }
        .metric-card:nth-child(1) { animation-delay: 0.1s; }
        .metric-card:nth-child(2) { animation-delay: 0.2s; }
        .metric-card:nth-child(3) { animation-delay: 0.3s; }
        .metric-card:nth-child(4) { animation-delay: 0.4s; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    metrics_html = '<div class="metrics-container">'
    for metric in metrics_data:
        icon_html = (
            f'<div class="metric-icon">{metric.get("icon", "")}</div>'
            if metric.get("icon")
            else ""
        )
        unit = metric.get("unit", "")
        unit_html = f'<span class="metric-unit">{unit}</span>' if unit else ""
        help_text = f'title="{metric.get("help")}"' if metric.get("help") else ""

        metrics_html += f"""
        <div class="metric-card" {help_text}>
            {icon_html}
            <div class="metric-value">{metric['value']}{unit_html}</div>
            <div class="metric-label">{metric['label']}</div>
        </div>
        """

    metrics_html += '</div>'
    st.markdown(metrics_html, unsafe_allow_html=True)

