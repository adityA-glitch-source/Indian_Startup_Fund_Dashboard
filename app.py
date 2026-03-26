import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(layout='wide', page_title='Indian Startup Funding Dashboard')

# ---------------------- HELPERS ----------------------
def normalize_text(x):
    x = str(x).lower()
    x = re.sub(r'[^a-z0-9\s]', '', x)
    x = re.sub(r'\s+', ' ', x).strip()
    return x

def format_cr(x):
    return f"₹{round(x,2)} Cr"

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv('startup_cleaned.csv')

    # -------- DATE --------
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # -------- AMOUNT --------
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    # -------- CITY CLEANING --------
    valid_cities = [
        'bangalore','bengaluru','mumbai','delhi','new delhi',
        'gurgaon','gurugram','hyderabad','pune','chennai',
        'kolkata','bhubaneswar','bhubneswar','andheri'
    ]

    def extract_city(x):
        x = normalize_text(x)
        parts = x.replace(',', '/').split('/')
        for part in parts:
            if part.strip() in valid_cities:
                return part.strip()
        return None

    df['city'] = df['city'].apply(extract_city)

    city_map = {
        'bengaluru': 'Bangalore','bangalore': 'Bangalore',
        'new delhi': 'Delhi','delhi': 'Delhi',
        'gurgaon': 'Gurgaon','gurugram': 'Gurgaon',
        'bhubneswar': 'Bhubaneswar','bhubaneswar': 'Bhubaneswar',
        'andheri': 'Mumbai'
    }

    df['city'] = df['city'].replace(city_map)
    df = df.dropna(subset=['city'])
    df['city'] = df['city'].str.title()

    # -------- SECTOR CLEANING --------
    df['vertical'] = df['vertical'].apply(normalize_text)

    sector_map = {
        'fintech': 'FinTech','finance': 'FinTech','financial services': 'FinTech',
        'edtech': 'EdTech','education': 'EdTech',
        'ecommerce': 'E-commerce','e commerce': 'E-commerce',
        'healthtech': 'HealthTech','healthcare': 'HealthTech',
        'ai': 'AI','machine learning': 'AI',
        'saas': 'SaaS','software': 'SaaS',
        'logistics': 'Logistics',
        'food': 'Food',
        'gaming': 'Gaming','agritech': 'AgriTech'
    }

    df['vertical'] = df['vertical'].replace(sector_map)
    df['vertical'] = df['vertical'].replace(['unknown','nan',''], 'Other')

    top_sectors = df['vertical'].value_counts().head(10).index
    df['vertical'] = df['vertical'].apply(lambda x: x if x in top_sectors else 'Other')

    # -------- STARTUP CLEANING --------
    df['startup'] = df['startup'].apply(normalize_text)

    startup_map = {
        'ola': 'Ola',
        'ola cabs': 'Ola',
        'flipkart': 'Flipkart',
        'flipkart online': 'Flipkart',
        'paytm': 'Paytm',
        'paytm payments': 'Paytm',
        'byju': 'Byju’s',
        'byjus': 'Byju’s'
    }

    def clean_startup(x):
        for key in startup_map:
            if key in x:
                return startup_map[key]
        return x.title()

    df['startup'] = df['startup'].apply(clean_startup)

    # -------- INVESTOR CLEANING --------
    df['investors'] = df['investors'].fillna("")

    def clean_investors(x):
        investors = x.split(',')
        cleaned = []

        for inv in investors:
            inv = normalize_text(inv)

            if 'sequoia' in inv:
                cleaned.append('Sequoia')
            elif 'accel' in inv:
                cleaned.append('Accel')
            elif 'softbank' in inv:
                cleaned.append('SoftBank')
            elif 'tiger global' in inv:
                cleaned.append('Tiger Global')
            elif 'matrix' in inv:
                cleaned.append('Matrix')
            elif inv != "":
                cleaned.append(inv.title())

        return list(set(cleaned))

    df['investor_list'] = df['investors'].apply(clean_investors)

    return df


df = load_data()
investor_df = df.explode('investor_list')
investor_df = investor_df.drop_duplicates(subset=['startup','investor_list','amount'])

# ---------------------- SIDEBAR ----------------------
st.sidebar.markdown("## 🔍 Filters")

year_filter = st.sidebar.multiselect("Year", sorted(df['year'].dropna().unique()))
city_filter = st.sidebar.multiselect("City", sorted(df['city'].dropna().unique()))
sector_filter = st.sidebar.multiselect("Sector", sorted(df['vertical'].dropna().unique()))

view = st.sidebar.radio("Select View", ["Overview", "Startup", "Investor"])

filtered_df = df.copy()

if year_filter:
    filtered_df = filtered_df[filtered_df['year'].isin(year_filter)]
if city_filter:
    filtered_df = filtered_df[filtered_df['city'].isin(city_filter)]
if sector_filter:
    filtered_df = filtered_df[filtered_df['vertical'].isin(sector_filter)]

filtered_investor_df = filtered_df.explode('investor_list')

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# ---------------------- HEADER ----------------------
st.markdown("""
<h1 style='text-align:center; color:#2E86C1;'>🇮🇳 Indian Startup Funding Dashboard</h1>
<p style='text-align:center;'>Analyze funding trends, sectors, and investor activity</p>
""", unsafe_allow_html=True)

# ---------------------- OVERVIEW ----------------------
def show_overview():
    total = filtered_df['amount'].sum()
    max_funding = filtered_df.groupby('startup')['amount'].max().max()
    avg_funding = filtered_df.groupby('startup')['amount'].sum().mean()
    startups = filtered_df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Funding", format_cr(total))
    col2.metric("Max Funding", format_cr(max_funding))
    col3.metric("Avg Funding", format_cr(avg_funding))
    col4.metric("Startups", startups)

    st.divider()

    # Trend
    trend = filtered_df.groupby(['year','month'])['amount'].sum().reset_index()
    trend['date'] = pd.to_datetime(trend[['year','month']].assign(day=1))
    st.plotly_chart(px.line(trend, x='date', y='amount', markers=True), use_container_width=True)

    # Sector
    sector = filtered_df.groupby('vertical')['amount'].sum().reset_index()
    st.plotly_chart(px.bar(sector, x='vertical', y='amount'), use_container_width=True)

    # City
    city = filtered_df.groupby('city')['amount'].sum().reset_index()
    st.plotly_chart(px.bar(city, x='city', y='amount'), use_container_width=True)

    # Map
    city_coords = {
        'Bangalore': (12.9716,77.5946),'Mumbai': (19.0760,72.8777),
        'Delhi': (28.6139,77.2090),'Gurgaon': (28.4595,77.0266),
        'Hyderabad': (17.3850,78.4867),'Pune': (18.5204,73.8567),
        'Chennai': (13.0827,80.2707),'Kolkata': (22.5726,88.3639),
        'Bhubaneswar': (20.2961,85.8245)
    }

    map_df = city.copy()
    map_df['lat'] = map_df['city'].apply(lambda x: city_coords.get(x,(None,None))[0])
    map_df['lon'] = map_df['city'].apply(lambda x: city_coords.get(x,(None,None))[1])
    map_df = map_df.dropna()

    st.plotly_chart(px.scatter_mapbox(
        map_df, lat='lat', lon='lon', size='amount',
        hover_name='city', zoom=4, mapbox_style='carto-positron'
    ), use_container_width=True)

    # Top Investors
    top_inv = filtered_investor_df.groupby('investor_list')['amount'].sum().reset_index().sort_values(by='amount',ascending=False).head(10)
    st.plotly_chart(px.bar(top_inv, x='investor_list', y='amount'), use_container_width=True)

# ---------------------- STARTUP ----------------------
def show_startup():
    startup = st.selectbox("Select Startup", sorted(filtered_df['startup'].unique()))
    data = filtered_df[filtered_df['startup']==startup]

    st.dataframe(data)
    yearly = data.groupby('year')['amount'].sum().reset_index()
    st.plotly_chart(px.line(yearly, x='year', y='amount', markers=True), use_container_width=True)

# ---------------------- INVESTOR ----------------------
def show_investor():
    investors = sorted([i for i in filtered_investor_df['investor_list'].dropna() if i!=""])
    investor = st.selectbox("Select Investor", investors)

    inv_df = filtered_investor_df[filtered_investor_df['investor_list']==investor]

    st.dataframe(inv_df.head())

    top = inv_df.groupby('startup')['amount'].sum().reset_index().sort_values(by='amount',ascending=False).head(10)
    st.plotly_chart(px.bar(top, x='startup', y='amount'), use_container_width=True)

    sector = inv_df.groupby('vertical')['amount'].sum().reset_index()
    st.plotly_chart(px.pie(sector, values='amount', names='vertical'), use_container_width=True)

# ---------------------- MAIN ----------------------
if view == "Overview":
    show_overview()
elif view == "Startup":
    show_startup()
else:
    show_investor()

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown("<p style='text-align:center;'>Built by Aditya Kumar</p>", unsafe_allow_html=True)
