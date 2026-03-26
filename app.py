import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide', page_title='Startup Funding Dashboard')

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv('startup_cleaned.csv')

    # Cleaning
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    df['investors'] = df['investors'].fillna("")
    df['investor_list'] = df['investors'].apply(lambda x: [i.strip() for i in x.split(',')])

    return df

df = load_data()

# Exploded investor dataframe
investor_df = df.explode('investor_list')

# ---------------------- HELPER ----------------------
def format_cr(x):
    return f"₹{round(x,2)} Cr"

# ---------------------- SIDEBAR ----------------------
st.sidebar.title("🔍 Filters")

year_filter = st.sidebar.multiselect("Year", sorted(df['year'].dropna().unique()))
city_filter = st.sidebar.multiselect("City", sorted(df['city'].dropna().unique()))
sector_filter = st.sidebar.multiselect("Sector", sorted(df['vertical'].dropna().unique()))

view = st.sidebar.radio("Select View", ["Overview", "Startup", "Investor"])

# Apply filters
filtered_df = df.copy()

if year_filter:
    filtered_df = filtered_df[filtered_df['year'].isin(year_filter)]

if city_filter:
    filtered_df = filtered_df[filtered_df['city'].isin(city_filter)]

if sector_filter:
    filtered_df = filtered_df[filtered_df['vertical'].isin(sector_filter)]

filtered_investor_df = filtered_df.explode('investor_list')

# ---------------------- OVERVIEW ----------------------
def show_overview():
    st.title("📊 Indian Startup Funding Dashboard")

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

    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🏭 Sectors", "🏙️ Cities"])

    # -------- Trends --------
    with tab1:
        trend = filtered_df.groupby(['year', 'month'])['amount'].sum().reset_index()
        trend['date'] = pd.to_datetime(trend[['year','month']].assign(day=1))

        fig = px.line(trend, x='date', y='amount', markers=True, title="Funding Trend")
        st.plotly_chart(fig, use_container_width=True)

    # -------- Sector --------
    with tab2:
        sector = filtered_df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)

        fig = px.bar(
            x=sector.index,
            y=sector.values,
            color=sector.index,
            title="Top Sectors"
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------- City --------
    with tab3:
        city = filtered_df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)

        fig = px.bar(
            x=city.index,
            y=city.values,
            color=city.index,
            title="Top Cities"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------- Investor Panel --------
    st.subheader("🏆 Top Investors")

    top_inv = filtered_investor_df.groupby('investor_list')['amount'].sum().sort_values(ascending=False).head(10)

    fig = px.bar(x=top_inv.index, y=top_inv.values)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------- Insights --------
    st.subheader("🧠 Key Insights")

    top_sector = filtered_df.groupby('vertical')['amount'].sum().idxmax()
    top_city = filtered_df.groupby('city')['amount'].sum().idxmax()
    top_investor = filtered_investor_df.groupby('investor_list')['amount'].sum().idxmax()

    st.write(f"📊 Top sector: **{top_sector}**")
    st.write(f"🏙️ Top city: **{top_city}**")
    st.write(f"💰 Most active investor: **{top_investor}**")


# ---------------------- STARTUP ----------------------
def show_startup():
    st.title("🏢 Startup Analysis")

    startup = st.selectbox("Select Startup", sorted(filtered_df['startup'].unique()))

    startup_df = filtered_df[filtered_df['startup'] == startup]

    st.subheader("Funding History")
    st.dataframe(startup_df)

    yearly = startup_df.groupby('year')['amount'].sum().reset_index()

    fig = px.line(yearly, x='year', y='amount', markers=True, title="Yearly Funding")
    st.plotly_chart(fig, use_container_width=True)


# ---------------------- INVESTOR ----------------------
def show_investor():
    st.title("💰 Investor Analysis")

    investors = sorted(set(filtered_investor_df['investor_list'].dropna()))
    investor = st.selectbox("Select Investor", investors)

    inv_df = filtered_investor_df[filtered_investor_df['investor_list'] == investor]

    st.subheader("Recent Investments")
    st.dataframe(inv_df[['date','startup','vertical','city','amount']].head())

    col1, col2 = st.columns(2)

    with col1:
        top = inv_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top.index, y=top.values, title="Top Investments")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sector = inv_df.groupby('vertical')['amount'].sum()
        fig2 = px.pie(values=sector.values, names=sector.index, title="Sector Distribution")
        st.plotly_chart(fig2)

    yearly = inv_df.groupby('year')['amount'].sum().reset_index()
    fig3 = px.line(yearly, x='year', y='amount', markers=True, title="Yearly Investment Trend")
    st.plotly_chart(fig3, use_container_width=True)


# ---------------------- MAIN ----------------------
if view == "Overview":
    show_overview()
elif view == "Startup":
    show_startup()
else:
    show_investor()
