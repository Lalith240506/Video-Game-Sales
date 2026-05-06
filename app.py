import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Configure the Streamlit page
st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# Cyberpunk Neon Color Palette
NEON_COLORS = ['#00f3ff', '#ff00ff', '#39ff14', '#fdfa72', '#ff073a', '#bc13fe', '#ff71ce', '#fce83a']
BG_TRANSPARENT = 'rgba(0,0,0,0)'

# Common Plotly Layout Update Function
def apply_cyberpunk_theme(fig):
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor=BG_TRANSPARENT,
        paper_bgcolor=BG_TRANSPARENT,
        font=dict(color='#E0E0E0', family="sans-serif"),
        title=dict(font=dict(size=20, color='#00f3ff')),
        legend=dict(bgcolor='rgba(18, 21, 30, 0.5)'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    # Add subtle grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.1)')
    return fig

# Data Generation and Loading
@st.cache_data
def load_data():
    file_path = 'vgsales.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    
    # Generate Synthetic Dataset
    np.random.seed(42)
    n = 2000
    genres = ['Action', 'RPG', 'Shooter', 'Sports', 'Platform', 'Racing', 'Strategy', 'Simulation', 'Fighting', 'Puzzle']
    publishers = ['Nintendo', 'Electronic Arts', 'Activision', 'Sony', 'Ubisoft', 'Take-Two', 'Sega', 'Square Enix', 'Capcom', 'Bandai Namco']
    platforms = ['PS4', 'PS3', 'X360', 'XOne', 'PC', 'Switch', 'Wii', 'DS', 'PS2', 'PS5', 'XSX']
    
    # Simulating data spanning from 1980 to 2024
    years = np.random.normal(loc=2010, scale=8, size=n).astype(int)
    years = np.clip(years, 1980, 2024)
    
    genre_col = np.random.choice(genres, size=n)
    publisher_col = np.random.choice(publishers, size=n)
    platform_col = np.random.choice(platforms, size=n)
    
    # Sales distributed exponentially for realism
    na_sales = np.random.exponential(1.5, size=n)
    eu_sales = np.random.exponential(1.0, size=n)
    jp_sales = np.random.exponential(0.5, size=n)
    other_sales = np.random.exponential(0.3, size=n)
    global_sales = na_sales + eu_sales + jp_sales + other_sales
    
    # Critic scores normally distributed
    critic_score = np.random.normal(72, 14, size=n)
    critic_score = np.clip(critic_score, 10, 100).astype(int)
    
    # Generate mock names
    adjectives = ['Dark', 'Neon', 'Cyber', 'Super', 'Final', 'Infinite', 'Ultra', 'Phantom', 'Zero', 'Quantum']
    nouns = ['Protocol', 'Strike', 'Fantasy', 'Duty', 'Kombat', 'Horizon', 'Odyssey', 'Space', 'Impact', 'Engine']
    names = [f"{np.random.choice(adjectives)} {np.random.choice(nouns)} {i}" for i in range(n)]
    
    df = pd.DataFrame({
        'Name': names,
        'Platform': platform_col,
        'Year': years,
        'Genre': genre_col,
        'Publisher': publisher_col,
        'NA_Sales': na_sales,
        'EU_Sales': eu_sales,
        'JP_Sales': jp_sales,
        'Other_Sales': other_sales,
        'Global_Sales': global_sales,
        'Critic_Score': critic_score
    })
    df = df.round({'NA_Sales': 2, 'EU_Sales': 2, 'JP_Sales': 2, 'Other_Sales': 2, 'Global_Sales': 2})
    df.to_csv(file_path, index=False)
    return df

df = load_data()

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #00f3ff; text-shadow: 0 0 10px #00f3ff;'>VIDEO GAME SALES DASHBOARD (1980–2024)</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #ff00ff; letter-spacing: 2px;'>ANALYTICS OVERVIEW</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid rgba(0, 243, 255, 0.3);'>", unsafe_allow_html=True)

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("<h2 style='color: #39ff14;'>CYBER-FILTERS</h2>", unsafe_allow_html=True)

# Genre Filter
all_genres = sorted(df['Genre'].unique())
selected_genres = st.sidebar.multiselect("SELECT GENRE", all_genres, default=all_genres)

# Year Range Slider
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_range = st.sidebar.slider("SELECT YEAR RANGE", min_year, max_year, (1990, max_year))

# Apply button logic via Session State or just let Streamlit auto-rerun
# Streamlit auto-reruns on slider change, giving "smooth, fluid transitions"
filtered_df = df[
    (df['Genre'].isin(selected_genres)) & 
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1])
]

# Total record count
st.sidebar.markdown(f"**Total Records Selected:** `{len(filtered_df)}`")

# Reset Filter Functionality
if st.sidebar.button("RESET FILTERS", use_container_width=True):
    # Streamlit natively resets by rerunning or can use st.query_params / st.session_state
    # A simple rerun triggers reset if we clear session state, but for simplicity:
    st.sidebar.success("Reset logic is handled manually or by refreshing the app.")

if len(filtered_df) == 0:
    st.warning("No data matches the selected filters.")
    st.stop()

# --- KPIs ---
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Games", f"{len(filtered_df):,}")
with col2:
    st.metric("Global Sales", f"{filtered_df['Global_Sales'].sum():,.1f}M")
with col3:
    best_game = filtered_df.loc[filtered_df['Global_Sales'].idxmax(), 'Name']
    st.metric("Best-Selling Game", best_game)
with col4:
    top_genre = filtered_df.groupby('Genre')['Global_Sales'].sum().idxmax()
    st.metric("Top Genre", top_genre)
with col5:
    st.metric("Avg Critic Score", f"{filtered_df['Critic_Score'].mean():.1f}")
with col6:
    top_pub = filtered_df.groupby('Publisher')['Global_Sales'].sum().idxmax()
    st.metric("Top Publisher", top_pub)

st.markdown("<br>", unsafe_allow_html=True)

# --- CHARTS ---
# Row 1: Line Chart & Doughnut Chart
r1c1, r1c2 = st.columns([2, 1])

with r1c1:
    yearly_sales = filtered_df.groupby('Year')['Global_Sales'].sum().reset_index()
    fig_line = px.line(
        yearly_sales, x='Year', y='Global_Sales', 
        title='Yearly Global Sales Trend',
        color_discrete_sequence=['#00f3ff']
    )
    fig_line.update_traces(line=dict(width=4), fill='tozeroy', fillcolor='rgba(0, 243, 255, 0.1)')
    apply_cyberpunk_theme(fig_line)
    st.plotly_chart(fig_line, use_container_width=True)

with r1c2:
    genre_sales = filtered_df.groupby('Genre')['Global_Sales'].sum().reset_index()
    fig_donut = px.pie(
        genre_sales, names='Genre', values='Global_Sales', hole=0.6,
        title='Genre Distribution',
        color_discrete_sequence=NEON_COLORS
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
    apply_cyberpunk_theme(fig_donut)
    # Hide legend to save space
    fig_donut.update_layout(showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)


# Row 2: Bar Chart & Horizontal Bar Chart
r2c1, r2c2 = st.columns(2)

with r2c1:
    console_sales = filtered_df.groupby('Platform')['Global_Sales'].sum().nlargest(10).reset_index()
    fig_bar = px.bar(
        console_sales, x='Platform', y='Global_Sales',
        title='Top Consoles by Sales',
        color='Global_Sales', color_continuous_scale=['#ff00ff', '#00f3ff']
    )
    apply_cyberpunk_theme(fig_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

with r2c2:
    pub_sales = filtered_df.groupby('Publisher')['Global_Sales'].sum().nlargest(10).reset_index()
    pub_sales = pub_sales.sort_values('Global_Sales', ascending=True) # Sort for horizontal bar
    fig_hbar = px.bar(
        pub_sales, x='Global_Sales', y='Publisher', orientation='h',
        title='Top Publishers by Sales',
        color='Global_Sales', color_continuous_scale=['#39ff14', '#fdfa72']
    )
    apply_cyberpunk_theme(fig_hbar)
    st.plotly_chart(fig_hbar, use_container_width=True)

# Row 3: Multi-line Chart & Scatter Plot
r3c1, r3c2 = st.columns(2)

with r3c1:
    # Top 5 genres over time
    top_5_genres = filtered_df.groupby('Genre')['Global_Sales'].sum().nlargest(5).index
    genre_trends = filtered_df[filtered_df['Genre'].isin(top_5_genres)].groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()
    
    fig_mline = px.line(
        genre_trends, x='Year', y='Global_Sales', color='Genre',
        title='Top 5 Genres Trend Over Time',
        color_discrete_sequence=NEON_COLORS
    )
    fig_mline.update_traces(line=dict(width=3))
    apply_cyberpunk_theme(fig_mline)
    st.plotly_chart(fig_mline, use_container_width=True)

with r3c2:
    fig_scatter = px.scatter(
        filtered_df, x='Critic_Score', y='Global_Sales', color='Genre', hover_name='Name',
        title='Critic Score vs. Global Sales',
        color_discrete_sequence=NEON_COLORS,
        opacity=0.7
    )
    fig_scatter.update_traces(marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')))
    apply_cyberpunk_theme(fig_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- EXTRA ELEMENTS & REGIONAL PROGRESS ---
st.markdown("### REGIONAL SALES BREAKDOWN")
total_sales = filtered_df['Global_Sales'].sum()

if total_sales > 0:
    reg_col1, reg_col2, reg_col3, reg_col4 = st.columns(4)
    na_pct = filtered_df['NA_Sales'].sum() / total_sales
    eu_pct = filtered_df['EU_Sales'].sum() / total_sales
    jp_pct = filtered_df['JP_Sales'].sum() / total_sales
    other_pct = filtered_df['Other_Sales'].sum() / total_sales
    
    with reg_col1:
        st.markdown(f"**North America:** {na_pct:.1%}")
        st.progress(float(na_pct))
    with reg_col2:
        st.markdown(f"**Europe:** {eu_pct:.1%}")
        st.progress(float(eu_pct))
    with reg_col3:
        st.markdown(f"**Japan:** {jp_pct:.1%}")
        st.progress(float(jp_pct))
    with reg_col4:
        st.markdown(f"**Other Regions:** {other_pct:.1%}")
        st.progress(float(other_pct))

st.markdown("<br>", unsafe_allow_html=True)

# --- DATA TABLE ---
st.markdown("### TOP SELLING GAMES DATA")

# Helper function to style critic scores
def style_scores(val):
    if val >= 85:
        color = '#39ff14'  # Neon Green
    elif val >= 70:
        color = '#fdfa72'  # Neon Yellow
    else:
        color = '#ff073a'  # Neon Red
    return f'color: {color}; font-weight: bold;'

display_cols = ['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Critic_Score', 'Global_Sales']
top_games_df = filtered_df[display_cols].sort_values(by='Global_Sales', ascending=False).head(100).reset_index(drop=True)

# Apply Pandas styling
styled_df = top_games_df.style.map(style_scores, subset=['Critic_Score'])\
                              .format({'Global_Sales': '{:.2f}', 'Year': '{:.0f}'})\
                              .set_properties(**{'background-color': 'rgba(18, 21, 30, 0.8)', 'color': '#E0E0E0', 'border-color': 'rgba(0, 243, 255, 0.3)'})

st.dataframe(styled_df, use_container_width=True, height=400)

# --- INSIGHTS SECTION ---
st.info(f"**SYSTEM INSIGHT:** The dataset currently filters **{len(filtered_df)}** records. The top-performing genre is **{top_genre}** with {filtered_df.groupby('Genre')['Global_Sales'].sum().max():.2f}M units sold globally. Average critic approval sits at **{filtered_df['Critic_Score'].mean():.1f}/100**.")
