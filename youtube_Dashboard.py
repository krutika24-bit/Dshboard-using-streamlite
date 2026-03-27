import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="▶️",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("youtube_data.csv")
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.title("🎛️ Filters")

all_categories = sorted(df["category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Category", all_categories, default=all_categories
)

all_countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Country", all_countries, default=all_countries
)

year_min, year_max = int(df["created_year"].min()), int(df["created_year"].max())
year_range = st.sidebar.slider("Channel Created Year", year_min, year_max, (year_min, year_max))

# ── Filter dataframe ──────────────────────────────────────────────────────────
filtered = df[
    df["category"].isin(selected_categories)
    & df["Country"].isin(selected_countries)
    & df["created_year"].between(*year_range)
]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("▶️ YouTube Top Channels Dashboard")
st.markdown(f"Showing **{len(filtered):,}** of **{len(df):,}** channels")
st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Channels", f"{len(filtered):,}")
k2.metric("Total Subscribers", f"{filtered['subscribers'].sum()/1e9:.2f}B")
k3.metric("Total Video Views", f"{filtered['video views'].sum()/1e12:.2f}T")
k4.metric("Avg Engagement Rate", f"{filtered['engagement_rate'].mean():.4f}")

st.divider()

# ── Row 1: Top YouTubers + Category Distribution ──────────────────────────────
col1, col2 = st.columns([1.4, 1])

with col1:
    st.subheader("🏆 Top 10 Channels by Subscribers")
    top10 = filtered.nlargest(10, "subscribers")[["Youtuber", "subscribers", "category", "Country"]]
    top10["subscribers_M"] = (top10["subscribers"] / 1e6).round(1)
    fig_bar = px.bar(
        top10.sort_values("subscribers"),
        x="subscribers_M",
        y="Youtuber",
        orientation="h",
        color="category",
        labels={"subscribers_M": "Subscribers (M)", "Youtuber": ""},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_bar.update_layout(showlegend=False, height=380, margin=dict(l=0, r=20, t=10, b=40))
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("📂 Channels by Category")
    cat_count = filtered["category"].value_counts().reset_index()
    cat_count.columns = ["category", "count"]
    fig_pie = px.pie(
        cat_count,
        values="count",
        names="category",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_pie.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 2: Subscribers vs Views scatter + Country bar ────────────────────────
col3, col4 = st.columns([1.3, 1])

with col3:
    st.subheader("📊 Subscribers vs Video Views")
    fig_scatter = px.scatter(
        filtered,
        x="subscribers",
        y="video views",
        color="category",
        hover_name="Youtuber",
        hover_data={"Country": True, "category": True},
        labels={"subscribers": "Subscribers", "video views": "Total Video Views"},
        color_discrete_sequence=px.colors.qualitative.Bold,
        opacity=0.75,
    )
    fig_scatter.update_layout(height=380, margin=dict(l=0, r=20, t=10, b=40))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col4:
    st.subheader("🌍 Top 10 Countries by Channels")
    top_countries = filtered["Country"].value_counts().nlargest(10).reset_index()
    top_countries.columns = ["Country", "count"]
    fig_country = px.bar(
        top_countries.sort_values("count"),
        x="count",
        y="Country",
        orientation="h",
        color="count",
        color_continuous_scale="Reds",
        labels={"count": "Number of Channels", "Country": ""},
    )
    fig_country.update_layout(
        coloraxis_showscale=False, height=380, margin=dict(l=0, r=20, t=10, b=40)
    )
    st.plotly_chart(fig_country, use_container_width=True)

# ── Row 3: Earnings + Channels over time ──────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("💰 Avg Highest Yearly Earnings by Category")
    earn = (
        filtered.groupby("category")["highest_yearly_earnings"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    earn.columns = ["category", "avg_earnings"]
    fig_earn = px.bar(
        earn,
        x="category",
        y="avg_earnings",
        color="category",
        labels={"avg_earnings": "Avg Yearly Earnings (USD)", "category": ""},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_earn.update_layout(showlegend=False, height=360, margin=dict(l=0, r=0, t=10, b=80))
    fig_earn.update_xaxes(tickangle=35)
    st.plotly_chart(fig_earn, use_container_width=True)

with col6:
    st.subheader("📅 Channels Created per Year")
    by_year = filtered["created_year"].value_counts().sort_index().reset_index()
    by_year.columns = ["Year", "Channels"]
    fig_line = px.line(
        by_year,
        x="Year",
        y="Channels",
        markers=True,
        color_discrete_sequence=["#E63946"],
    )
    fig_line.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=40))
    st.plotly_chart(fig_line, use_container_width=True)

# ── Row 4: Engagement rate by category ───────────────────────────────────────
st.subheader("⚡ Engagement Rate by Category")
engage = filtered.groupby("category")["engagement_rate"].mean().sort_values(ascending=False).reset_index()
fig_eng = px.bar(
    engage,
    x="category",
    y="engagement_rate",
    color="engagement_rate",
    color_continuous_scale="Teal",
    labels={"engagement_rate": "Avg Engagement Rate", "category": ""},
)
fig_eng.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=0, r=0, t=10, b=60))
fig_eng.update_xaxes(tickangle=25)
st.plotly_chart(fig_eng, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────────────────────
st.divider()
with st.expander("🗃️ View Raw Data"):
    st.dataframe(
        filtered[["rank", "Youtuber", "category", "Country", "subscribers",
                  "video views", "highest_yearly_earnings", "engagement_rate"]].reset_index(drop=True),
        use_container_width=True,
    )
