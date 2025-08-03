import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ✅ Fixed Render backend URL:
API_BASE = "https://where-did-my-tax-go-backend.onrender.com"

# Session state for theme toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Theme-based styling (same as your original)
def get_styles():
    if st.session_state.dark_mode:
        return {
            "bg_color": "#1e1e2f",
            "text_color": "white",
            "input_bg": "#2c2c3c",
            "button_color": "#b2d3f5",
            "chart_palette": px.colors.sequential.RdBu,
            "table_style": "color: white; background-color: #1e1e2f;",
            "select_year_color": "white",
            "bar_axis_color": "white",
        }
    else:
        return {
            "bg_color": "#f4f9f9",
            "text_color": "#222222",
            "input_bg": "#e4f0f5",
            "button_color": "#bae0da",
            "chart_palette": px.colors.sequential.Teal,
            "table_style": "color: #222222; background-color: #fdfdfd;",
            "select_year_color": "black",
            "bar_axis_color": "black",
        }

styles = get_styles()

# Inject styles (same as your original)
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {styles['bg_color']};
            color: {styles['text_color']};
        }}
        .stTextInput > div > div > input,
        .stSelectbox > div {{
            background-color: {styles['input_bg']} !important;
            color: {styles['text_color']} !important;
        }}
        .stButton > button {{
            background-color: {styles['button_color']} !important;
            color: black !important;
            border: none;
        }}
        .stDataFrame tbody td {{
            {styles['table_style']}
        }}
        label:has(div:has-text("Total Annual Tax Paid (₹)")),
        label:has(div:has-text("Choose Chart Type")) {{
            color: white !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("Tax Input 💰")
if st.sidebar.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.experimental_rerun()

# Input widgets
tax_input = st.sidebar.number_input("Total Annual Tax Paid (₹)", min_value=100, value=100000, step=100)
chart_type = st.sidebar.selectbox("Choose Chart Type", ["Pie Chart", "Bar Chart"])
st.sidebar.button("📊 Show Charts")

# Header
st.markdown("## 📊 Where Did My Tax Go?")

# Fetch available years from API
try:
    years_response = requests.get(f"{API_BASE}/api/years")
    years_response.raise_for_status()
    years = sorted(years_response.json(), reverse=True)
except Exception as e:
    st.error("Failed to fetch available years from API.")
    st.stop()

# Year selection
select_year_label = (
    f"<label style='color:{styles['select_year_color']}; font-weight:600; font-size:16px;'>📅 Select Year</label>"
)
st.markdown(select_year_label, unsafe_allow_html=True)
selected_year = st.selectbox("", years, label_visibility="collapsed")

# Fetch budget data for selected year from API
if selected_year:
    try:
        res = requests.get(f"{API_BASE}/api/budget/{selected_year}")
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        st.error("Failed to fetch budget data for the selected year.")
        st.stop()

    df = pd.DataFrame(data)
    df["Allocated Amount (₹)"] = (df["percent"] / 100) * tax_input
    df["percent"] = df["percent"].map(lambda x: f"{x:.1f}%")

    st.markdown("## 🧾 Tax Allocation Table")
    st.dataframe(df[["sector", "percent", "Allocated Amount (₹)"]], use_container_width=True)

    chart_data = df.copy()
    chart_data["amount"] = chart_data["Allocated Amount (₹)"]

    # Chart rendering
    if chart_type == "Pie Chart":
        fig = px.pie(
            chart_data,
            names="sector",
            values="amount",
            color_discrete_sequence=styles["chart_palette"]
        )
    else:
        fig = px.bar(
            chart_data,
            x="sector",
            y="amount",
            color="sector",
            color_discrete_sequence=styles["chart_palette"],
            height=400
        )
        fig.update_layout(
            height=400,
            margin=dict(t=40, b=40),
            paper_bgcolor=styles["bg_color"],
            plot_bgcolor=styles["bg_color"],
            font=dict(color=styles["text_color"]),
            xaxis=dict(
                tickfont=dict(color=styles["text_color"]),
                title_font=dict(color=styles["text_color"])
            ),
            yaxis=dict(
                tickfont=dict(color=styles["text_color"]),
                title_font=dict(color=styles["text_color"])
            ),
            showlegend=False
        )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📌 Chart Breakdown")
    st.dataframe(chart_data[["sector", "amount", "percent"]], use_container_width=True)
