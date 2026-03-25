import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Global Impact Dashboard", layout="wide")

# 2. CUSTOM CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #00ffcc; }
    [data-testid="stMetricDelta"] { font-size: 16px !important; }
    .stMetric {
        background-color: #1e2130;
        padding: 20px !important;
        border-radius: 12px;
        border: 1px solid #3e445e;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    hr { margin-top: 1rem; margin-bottom: 1rem; border-color: #3e445e; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA LOADING
@st.cache_data
def load_data():
    df = pd.read_csv("ai_company_adoption.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 4. MAIN TITLE
st.title("🤖 Global AI Adoption & Workforce Impact")
st.markdown("Financial and operational analysis of AI adoption by company size.")
st.markdown("---")

# 5. SIDEBAR FILTERS
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Filter A: Countries
    countries_list = sorted(df['country'].unique())
    selected_countries = st.multiselect(
        "1. Select Countries:",
        options=countries_list,
        default=countries_list[:8]
    )
    
    st.markdown("---")
    
    # Filter B: Industry (Select Slider)
    industries = ["All"] + sorted(df['industry'].unique().tolist())
    selected_industry = st.select_slider(
        "2. Industrial Sector:",
        options=industries,
        value="All"
    )

# 6. FILTERING LOGIC
df_filtered = df[df['country'].isin(selected_countries)]

if selected_industry != "All":
    df_filtered = df_filtered[df_filtered['industry'] == selected_industry]

# 7. KPI RENDER FUNCTION (ENGLISH VERSION)
def render_kpi_block(title, size_key):
    sub_df = df_filtered[df_filtered['company_size'] == size_key]
    
    st.subheader(title)
    
    if not sub_df.empty:
        col1, col2, col3 = st.columns(3)
        
        # KPI 1: Productivity (%)
        with col1:
            prod_avg = sub_df['productivity_change_percent'].mean()
            st.metric(
                label="📈 Avg. Productivity", 
                value=f"{prod_avg:.1f}%", 
                delta="Operational Gain"
            )
        
        # KPI 2: Revenue (USD Millions as main, % as delta)
        with col2:
            total_rev = sub_df['annual_revenue_usd_millions'].sum()
            rev_growth_pct = sub_df['revenue_growth_percent'].mean()
            st.metric(
                label="💰 Total Revenue", 
                value=f"${total_rev:,.0f}M", 
                delta=f"{rev_growth_pct:.1f}% Growth"
            )
            
        # KPI 3: Cost Savings (Estimated USD as main, % as delta)
        with col3:
            cost_red_pct = sub_df['cost_reduction_percent'].mean()
            # Calculation: Total Revenue * % Cost Reduction
            estimated_savings = (total_rev * cost_red_pct) / 100
            st.metric(
                label="📉 Cost Savings", 
                value=f"${estimated_savings:,.1f}M", 
                delta=f"-{cost_red_pct:.1f}% Reduction",
                delta_color="normal"
            )
    else:
        st.info(f"💡 No data available for '{size_key}' with current filters.")
    st.markdown("<br>", unsafe_allow_html=True)

# 8. SECTION RENDERING (Enterprise, SME, Startup)
render_kpi_block("🏢 Enterprise (Large Companies)", "Enterprise")
st.markdown("---")
render_kpi_block("🏢 SME (Medium Companies)", "SME")
st.markdown("---")
render_kpi_block("🚀 Startup", "Startup")

# 9. INTERACTIVE GEOGRAPHIC MAP
st.markdown("---")
st.subheader("🌐 Global Productivity Impact Map")

if not df_filtered.empty:
    fig = px.choropleth(
        df_filtered,
        locations="country",
        locationmode='country names',
        color="productivity_change_percent",
        hover_name="country",
        hover_data={
            'country': False,
            'industry': True,
            'ai_adoption_rate': True,
            'productivity_change_percent': ':.1f'
        },
        labels={'productivity_change_percent': 'Prod. %', 'ai_adoption_rate': 'AI Adoption'},
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#0e1117')
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Please select at least one country to display the map.")

st.caption(f"Current Filters | Industry: {selected_industry} | Countries: {len(selected_countries)}")