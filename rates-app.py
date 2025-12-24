import streamlit as st
import pandas as pd
import plotly.express as px
from fredapi import Fred


fred = Fred(api_key= st.secrets["fred_api_key"]

st.set_page_config(page_title="Interest Rate Dashboard", layout="wide")
st.title("📈 Interest Rate Dashboard")


# =========================
# HELPERS
# =========================
@st.cache_data
def load_series(series_id):
    return fred.get_series(series_id)

def make_df(series_dict):
    df = pd.DataFrame(series_dict)
    df.index = pd.to_datetime(df.index)
    return df.dropna()



# =========================
# LOAD DATA
# =========================

# US Yield Curve
yields = make_df({
    "2Y": load_series("DGS2"),
    "5Y": load_series("DGS5"),
    "10Y": load_series("DGS10"),
    "30Y": load_series("DGS30"),
})

# SOFR & Policy Rates
policy_rates = make_df({
    "SOFR": load_series("SOFR"),
    "ESTR": load_series("ECBESTRVOLWGTTRMDMNRT"),
    "Canada O/N": load_series("IRSTCI01CAM156N"),
})



# Real Yields (TIPS)
real_yields = make_df({
    "5Y Real": load_series("DFII5"),
    "10Y Real": load_series("DFII10"),
})

# --- Equity Indices
equities = make_df({
    "S&P 500": load_series("SP500"),
    "Dow Jones": load_series("DJIA"),
    "Nasdaq": load_series("NASDAQCOM"),
})




# =========================
# PRE-COMPUTE FIGURES
# =========================

# Heatmap
heatmap_data = yields.diff().tail(20)
fig_heatmap = px.imshow(
    heatmap_data.T,
    aspect="auto",
    color_continuous_scale="RdYlGn_r",
    title="Daily Yield Changes (bps)"
)

# Yield Curve Spreads
yields["2s10s"] = yields["10Y"] - yields["2Y"]
yields["5s30s"] = yields["30Y"] - yields["5Y"]

fig_curve = px.line(
    yields[["2s10s", "5s30s"]],
    title="Yield Curve Spreads (Steepening vs Flattening)"
)

# 10Y Yield
fig_10y = px.line(
    yields["10Y"],
    title="10Y Treasury Yield"
)

# SOFR Implied Rate
policy_rates["Implied SOFR"] = 100 - policy_rates["SOFR"]
fig_sofr = px.line(
    policy_rates["Implied SOFR"],
    title="Implied Policy Rate from SOFR"
)

# Real Yields
fig_real = px.line(
    real_yields,
    title="US Real Yields (TIPS)"
)

# Policy Divergence
policy_rates["SOFR - ESTR"] = policy_rates["SOFR"] - policy_rates["ESTR"]
policy_rates["SOFR - Canada"] = policy_rates["SOFR"] - policy_rates["Canada O/N"]

fig_div = px.line(
    policy_rates[["SOFR - ESTR", "SOFR - Canada"]],
    title="Policy Rate Spreads"
)


# =========================
# DASHBOARD LAYOUT
# =========================

st.header("📊 Rates Overview")

col_left, col_right = st.columns(2)

# -------- LEFT COLUMN --------
with col_left:
    st.subheader("10Y Treasury Yield")
    st.plotly_chart(fig_10y, use_container_width=True)

    st.subheader("Yield Curve Shape")
    st.plotly_chart(fig_curve, use_container_width=True)

    st.subheader("Real Yields")
    st.plotly_chart(fig_real, use_container_width=True)


# -------- RIGHT COLUMN --------
with col_right:
    st.subheader("Implied SOFR Policy Rate")
    st.plotly_chart(fig_sofr, use_container_width=True)

    st.subheader("Policy Divergence")
    st.plotly_chart(fig_div, use_container_width=True)

    st.subheader("Rate Move Heatmap")
    st.plotly_chart(fig_heatmap, use_container_width=True)



# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("Data source: **FRED** | Built for macro & rates analysis")
