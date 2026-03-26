import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(layout='wide', page_title='Indian Startup Funding Dashboard')

# ---------------------- NORMALIZATION ----------------------
def normalize_text(x):
    x = str(x).lower()
    x = re.sub(r'[^a-z0-9\s]', '', x)

    noise_words = [
        'partners','capital','ventures','investments','fund',
        'technology','opportunities','others','and','through','crowd','ing'
    ]

    for word in noise_words:
        x = x.replace(word, '')

    x = re.sub(r'\s+', ' ', x).strip()
    return x

def format_cr(x):
    return f"₹{round(x,2)} Cr"

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv('startup_cleaned.csv')

    # DATE
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # AMOUNT
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    # ---------------- CITY ----------------
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

    # ---------------- SECTOR ----------------
    df['vertical'] = df['vertical'].apply(normalize_text)

    sector_map = {
        'fintech': 'FinTech','finance': 'FinTech',
        'edtech': 'EdTech','education': 'EdTech',
        'ecommerce': 'E-commerce',
        'healthtech': 'HealthTech',
        'ai': 'AI',
        'saas': 'SaaS',
        'logistics': 'Logistics',
        'food': 'Food',
        'gaming': 'Gaming',
        'agritech': 'AgriTech'
    }

    df['vertical'] = df['vertical'].replace(sector_map)
    df['vertical'] = df['vertical'].replace(['unknown','nan',''], 'Other')

    top_sectors = df['vertical'].value_counts().head(10).index
    df['vertical'] = df['vertical'].apply(lambda x: x if x in top_sectors else 'Other')

    # ---------------- STARTUP ----------------
    df['startup'] = df['startup'].apply(normalize_text)

    startup_map = {
        'ola': 'Ola',
        'flipkart': 'Flipkart',
        'paytm': 'Paytm',
        'byju': 'Byju’s',
        'byjus': 'Byju’s'
    }

    def clean_startup(x):
        for key in startup_map:
            if key in x:
                return startup_map[key]
        return x.title()

    df['startup'] = df['startup'].apply(clean_startup)

    # ---------------- INVESTORS ----------------
    df['investors'] = df['investors'].fillna("")

    def clean_investors(x):
        investors = x.split(',')
        cleaned = []

        for inv in investors:
            inv = normalize_text(inv)

            # REMOVE JUNK
            if inv in ['', 'br']:
                continue
            if 'undisclosed' in inv or 'hni' in inv:
                continue

            # ENTITY GROUPING
            elif '1crowd' in inv:
                cleaned.append('1Crowd')

            elif '3one4' in inv:
                cleaned.append('3One4 Capital')

            elif '500' in inv:
                cleaned.append('500 Startups')

            elif 'accel' in inv:
                cleaned.append('Accel')

            elif 'ah' in inv:
                cleaned.append('Ah Ventures')

            elif 'bessemer' in inv:
                cleaned.append('Bessemer Venture Partners')

            elif 'blume' in inv:
                cleaned.append('Blume Ventures')

            elif 'beenext' in inv:
                cleaned.append('Beenext')

            elif 'beenos' in inv:
                cleaned.append('Beenos')

            elif 'matrix' in inv:
                cleaned.append('Matrix')

            elif 'lightspeed' in inv:
                cleaned.append('Lightspeed')

            elif 'kalaari' in inv:
                cleaned.append('Kalaari Capital')

            elif 'idg' in inv:
                cleaned.append('IDG Ventures')

            elif 'helion' in inv:
                cleaned.append('Helion Venture Partners')

            elif 'growx' in inv:
                cleaned.append('GrowX Ventures')

            elif 'letsventure' in inv:
                cleaned.append('LetsVenture')

            elif 'aarin' in inv:
                cleaned.append('Aarin Capital')

            elif 'zodius' in inv:
                cleaned.append('Zodius')

            elif 'zishaan hayath' in inv:
                cleaned.append('Zishaan Hayath')

            elif 'binny bansal' in inv:
                cleaned.append('Binny Bansal')

            elif 'american express' in inv:
                cleaned.append('American Express')

            elif 'anupam mittal' in inv:
                cleaned.append('Anupam Mittal')

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
    startups = filtered_df['startup'].nunique()

    col1, col2 = st.columns(2)
    col1.metric("Total Funding", format_cr(total))
    col2.metric("Startups", startups)

    trend = filtered_df.groupby(['year','month'])['amount'].sum().reset_index()
    trend['date'] = pd.to_datetime(trend[['year','month']].assign(day=1))
    st.plotly_chart(px.line(trend, x='date', y='amount'), use_container_width=True)

    sector = filtered_df.groupby('vertical')['amount'].sum().reset_index()
    st.plotly_chart(px.bar(sector, x='vertical', y='amount'), use_container_width=True)

    city = filtered_df.groupby('city')['amount'].sum().reset_index()
    st.plotly_chart(px.bar(city, x='city', y='amount'), use_container_width=True)

# ---------------------- STARTUP ----------------------
def show_startup():
    startup = st.selectbox("Startup", sorted(filtered_df['startup'].unique()))
    data = filtered_df[filtered_df['startup']==startup]

    st.dataframe(data)
    yearly = data.groupby('year')['amount'].sum().reset_index()
    st.plotly_chart(px.line(yearly, x='year', y='amount'), use_container_width=True)

# ---------------------- INVESTOR ----------------------
def show_investor():
    investors = sorted(set(filtered_investor_df['investor_list']))
    investor = st.selectbox("Investor", investors)

    inv_df = filtered_investor_df[filtered_investor_df['investor_list']==investor]

    st.dataframe(inv_df.head())

    top = inv_df.groupby('startup')['amount'].sum().reset_index()
    st.plotly_chart(px.bar(top, x='startup', y='amount'), use_container_width=True)

# ---------------------- MAIN ----------------------
if view == "Overview":
    show_overview()
elif view == "Startup":
    show_startup()
else:
    show_investor()

st.markdown("---")
st.markdown("<p style='text-align:center;'>Built by Aditya Kumar</p>", unsafe_allow_html=True)
