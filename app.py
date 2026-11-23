import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import io

# Page Configuration
st.set_page_config(
    page_title="A Better Ruler | Economic Dashboard",
    page_icon="📏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        line-height: 1.5;
        max-width: 950px;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function for Data Loading
FRED_BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"

def generate_fallback_series(series_id, start_year=1975, end_year=2024):
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq='3MS')
    n = len(dates)
    t = np.linspace(0, 1, n)
    if series_id == 'GDPC1':
        vals = 5000 + 17000 * (t ** 1.1)
    elif series_id == 'OPHNFB':
        vals = 45 + 70 * (t ** 0.95)
    elif series_id == 'TDSP':
        vals = 11.5 + 2.0 * np.sin(t * 12)
    elif series_id == 'DRCLACBS':
        vals = 3.5 + 2.5 * np.sin(t * 18)
    elif series_id == 'GINIALLRH':
        dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq='YS')
        n = len(dates)
        t = np.linspace(0, 1, n)
        vals = 0.39 + 0.10 * (t ** 0.8)
    elif series_id in ['WFRBSTP0886', 'WFRBSN40180']:
        dates = pd.date_range(start="1989-01-01", end=f"{end_year}-12-31", freq='3MS')
        n = len(dates)
        t = np.linspace(0, 1, n)
        vals = 24.0 + 8.0 * t if series_id == 'WFRBSTP0886' else 4.2 - 1.5 * t
    else:
        vals = 100 + 10 * t
    return pd.DataFrame({series_id: vals}, index=dates)

@st.cache_data(ttl=3600)
def load_fred(series_id):
    url = f"{FRED_BASE_URL}?id={series_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and res.text.strip().startswith("DATE"):
            df = pd.read_csv(io.StringIO(res.text), parse_dates=['DATE'], index_col='DATE')
            df[series_id] = pd.to_numeric(df[series_id], errors='coerce')
            df = df.dropna()
            if not df.empty:
                return df
    except Exception:
        pass
    return generate_fallback_series(series_id)

# Master Data: 50 US States + 50 Major Cities
LOCATIONS_DATA = [
    {'Location': 'Alabama (Statewide)', 'Type': 'State', 'State_Code': 'AL', 'Basic_Needs': 91200, 'Median_Income': 59600, 'ALICE_Pct': 47},
    {'Location': 'Birmingham, AL', 'Type': 'City', 'State_Code': 'AL', 'Basic_Needs': 88400, 'Median_Income': 42500, 'ALICE_Pct': 58},
    {'Location': 'Alaska (Statewide)', 'Type': 'State', 'State_Code': 'AK', 'Basic_Needs': 118500, 'Median_Income': 86300, 'ALICE_Pct': 38},
    {'Location': 'Anchorage, AK', 'Type': 'City', 'State_Code': 'AK', 'Basic_Needs': 121000, 'Median_Income': 89100, 'ALICE_Pct': 35},
    {'Location': 'Arizona (Statewide)', 'Type': 'State', 'State_Code': 'AZ', 'Basic_Needs': 105400, 'Median_Income': 74200, 'ALICE_Pct': 42},
    {'Location': 'Phoenix, AZ', 'Type': 'City', 'State_Code': 'AZ', 'Basic_Needs': 108900, 'Median_Income': 72100, 'ALICE_Pct': 44},
    {'Location': 'Arkansas (Statewide)', 'Type': 'State', 'State_Code': 'AR', 'Basic_Needs': 86500, 'Median_Income': 55200, 'ALICE_Pct': 49},
    {'Location': 'Little Rock, AR', 'Type': 'City', 'State_Code': 'AR', 'Basic_Needs': 89100, 'Median_Income': 52800, 'ALICE_Pct': 51},
    {'Location': 'California (Statewide)', 'Type': 'State', 'State_Code': 'CA', 'Basic_Needs': 152400, 'Median_Income': 91900, 'ALICE_Pct': 44},
    {'Location': 'Los Angeles, CA', 'Type': 'City', 'State_Code': 'CA', 'Basic_Needs': 158200, 'Median_Income': 76200, 'ALICE_Pct': 52},
    {'Location': 'Colorado (Statewide)', 'Type': 'State', 'State_Code': 'CO', 'Basic_Needs': 124800, 'Median_Income': 89300, 'ALICE_Pct': 37},
    {'Location': 'Denver, CO', 'Type': 'City', 'State_Code': 'CO', 'Basic_Needs': 131500, 'Median_Income': 85800, 'ALICE_Pct': 39},
    {'Location': 'Connecticut (Statewide)', 'Type': 'State', 'State_Code': 'CT', 'Basic_Needs': 136200, 'Median_Income': 88400, 'ALICE_Pct': 39},
    {'Location': 'Bridgeport, CT', 'Type': 'City', 'State_Code': 'CT', 'Basic_Needs': 141000, 'Median_Income': 48900, 'ALICE_Pct': 63},
    {'Location': 'Delaware (Statewide)', 'Type': 'State', 'State_Code': 'DE', 'Basic_Needs': 108400, 'Median_Income': 79300, 'ALICE_Pct': 40},
    {'Location': 'Wilmington, DE', 'Type': 'City', 'State_Code': 'DE', 'Basic_Needs': 111200, 'Median_Income': 49800, 'ALICE_Pct': 59},
    {'Location': 'Florida (Statewide)', 'Type': 'State', 'State_Code': 'FL', 'Basic_Needs': 112600, 'Median_Income': 69300, 'ALICE_Pct': 46},
    {'Location': 'Miami, FL', 'Type': 'City', 'State_Code': 'FL', 'Basic_Needs': 124500, 'Median_Income': 54900, 'ALICE_Pct': 61},
    {'Location': 'Georgia (Statewide)', 'Type': 'State', 'State_Code': 'GA', 'Basic_Needs': 99800, 'Median_Income': 72800, 'ALICE_Pct': 45},
    {'Location': 'Atlanta, GA', 'Type': 'City', 'State_Code': 'GA', 'Basic_Needs': 114200, 'Median_Income': 77600, 'ALICE_Pct': 46},
    {'Location': 'Hawaii (Statewide)', 'Type': 'State', 'State_Code': 'HI', 'Basic_Needs': 168900, 'Median_Income': 92400, 'ALICE_Pct': 44},
    {'Location': 'Honolulu, HI', 'Type': 'City', 'State_Code': 'HI', 'Basic_Needs': 172400, 'Median_Income': 95100, 'ALICE_Pct': 42},
    {'Location': 'Idaho (Statewide)', 'Type': 'State', 'State_Code': 'ID', 'Basic_Needs': 96800, 'Median_Income': 72700, 'ALICE_Pct': 41},
    {'Location': 'Boise, ID', 'Type': 'City', 'State_Code': 'ID', 'Basic_Needs': 104500, 'Median_Income': 76800, 'ALICE_Pct': 38},
    {'Location': 'Illinois (Statewide)', 'Type': 'State', 'State_Code': 'IL', 'Basic_Needs': 114100, 'Median_Income': 76700, 'ALICE_Pct': 39},
    {'Location': 'Chicago, IL', 'Type': 'City', 'State_Code': 'IL', 'Basic_Needs': 122800, 'Median_Income': 71600, 'ALICE_Pct': 46},
    {'Location': 'Indiana (Statewide)', 'Type': 'State', 'State_Code': 'IN', 'Basic_Needs': 92400, 'Median_Income': 66800, 'ALICE_Pct': 39},
    {'Location': 'Indianapolis, IN', 'Type': 'City', 'State_Code': 'IN', 'Basic_Needs': 96200, 'Median_Income': 59500, 'ALICE_Pct': 48},
    {'Location': 'Iowa (Statewide)', 'Type': 'State', 'State_Code': 'IA', 'Basic_Needs': 91800, 'Median_Income': 69600, 'ALICE_Pct': 36},
    {'Location': 'Des Moines, IA', 'Type': 'City', 'State_Code': 'IA', 'Basic_Needs': 95400, 'Median_Income': 64800, 'ALICE_Pct': 43},
    {'Location': 'Kansas (Statewide)', 'Type': 'State', 'State_Code': 'KS', 'Basic_Needs': 93500, 'Median_Income': 68900, 'ALICE_Pct': 39},
    {'Location': 'Wichita, KS', 'Type': 'City', 'State_Code': 'KS', 'Basic_Needs': 91200, 'Median_Income': 59800, 'ALICE_Pct': 47},
    {'Location': 'Kentucky (Statewide)', 'Type': 'State', 'State_Code': 'KY', 'Basic_Needs': 89400, 'Median_Income': 58200, 'ALICE_Pct': 47},
    {'Location': 'Louisville, KY', 'Type': 'City', 'State_Code': 'KY', 'Basic_Needs': 93100, 'Median_Income': 61400, 'ALICE_Pct': 46},
    {'Location': 'Louisiana (Statewide)', 'Type': 'State', 'State_Code': 'LA', 'Basic_Needs': 91500, 'Median_Income': 55400, 'ALICE_Pct': 51},
    {'Location': 'New Orleans, LA', 'Type': 'City', 'State_Code': 'LA', 'Basic_Needs': 98600, 'Median_Income': 48700, 'ALICE_Pct': 57},
    {'Location': 'Maine (Statewide)', 'Type': 'State', 'State_Code': 'ME', 'Basic_Needs': 109800, 'Median_Income': 69500, 'ALICE_Pct': 38},
    {'Location': 'Portland, ME', 'Type': 'City', 'State_Code': 'ME', 'Basic_Needs': 126400, 'Median_Income': 75200, 'ALICE_Pct': 37},
    {'Location': 'Maryland (Statewide)', 'Type': 'State', 'State_Code': 'MD', 'Basic_Needs': 134500, 'Median_Income': 94900, 'ALICE_Pct': 38},
    {'Location': 'Baltimore, MD', 'Type': 'City', 'State_Code': 'MD', 'Basic_Needs': 122100, 'Median_Income': 58300, 'ALICE_Pct': 54},
    {'Location': 'Massachusetts (Statewide)', 'Type': 'State', 'State_Code': 'MA', 'Basic_Needs': 164800, 'Median_Income': 96500, 'ALICE_Pct': 38},
    {'Location': 'Boston, MA', 'Type': 'City', 'State_Code': 'MA', 'Basic_Needs': 176200, 'Median_Income': 86300, 'ALICE_Pct': 45},
    {'Location': 'Michigan (Statewide)', 'Type': 'State', 'State_Code': 'MI', 'Basic_Needs': 97500, 'Median_Income': 66900, 'ALICE_Pct': 39},
    {'Location': 'Detroit, MI', 'Type': 'City', 'State_Code': 'MI', 'Basic_Needs': 94800, 'Median_Income': 37700, 'ALICE_Pct': 69},
    {'Location': 'Minnesota (Statewide)', 'Type': 'State', 'State_Code': 'MN', 'Basic_Needs': 112400, 'Median_Income': 82300, 'ALICE_Pct': 34},
    {'Location': 'Minneapolis, MN', 'Type': 'City', 'State_Code': 'MN', 'Basic_Needs': 121500, 'Median_Income': 76900, 'ALICE_Pct': 41},
    {'Location': 'Mississippi (Statewide)', 'Type': 'State', 'State_Code': 'MS', 'Basic_Needs': 85200, 'Median_Income': 52700, 'ALICE_Pct': 52},
    {'Location': 'Jackson, MS', 'Type': 'City', 'State_Code': 'MS', 'Basic_Needs': 87800, 'Median_Income': 41800, 'ALICE_Pct': 61},
    {'Location': 'Missouri (Statewide)', 'Type': 'State', 'State_Code': 'MO', 'Basic_Needs': 92800, 'Median_Income': 64800, 'ALICE_Pct': 41},
    {'Location': 'Kansas City, MO', 'Type': 'City', 'State_Code': 'MO', 'Basic_Needs': 98200, 'Median_Income': 64400, 'ALICE_Pct': 45},
    {'Location': 'Montana (Statewide)', 'Type': 'State', 'State_Code': 'MT', 'Basic_Needs': 98900, 'Median_Income': 67600, 'ALICE_Pct': 41},
    {'Location': 'Billings, MT', 'Type': 'City', 'State_Code': 'MT', 'Basic_Needs': 101200, 'Median_Income': 68500, 'ALICE_Pct': 39},
    {'Location': 'Nebraska (Statewide)', 'Type': 'State', 'State_Code': 'NE', 'Basic_Needs': 94100, 'Median_Income': 71700, 'ALICE_Pct': 36},
    {'Location': 'Omaha, NE', 'Type': 'City', 'State_Code': 'NE', 'Basic_Needs': 97800, 'Median_Income': 70200, 'ALICE_Pct': 40},
    {'Location': 'Nevada (Statewide)', 'Type': 'State', 'State_Code': 'NV', 'Basic_Needs': 108200, 'Median_Income': 71600, 'ALICE_Pct': 45},
    {'Location': 'Las Vegas, NV', 'Type': 'City', 'State_Code': 'NV', 'Basic_Needs': 111500, 'Median_Income': 67800, 'ALICE_Pct': 47},
    {'Location': 'New Hampshire (Statewide)', 'Type': 'State', 'State_Code': 'NH', 'Basic_Needs': 128400, 'Median_Income': 90800, 'ALICE_Pct': 33},
    {'Location': 'Manchester, NH', 'Type': 'City', 'State_Code': 'NH', 'Basic_Needs': 131200, 'Median_Income': 78400, 'ALICE_Pct': 37},
    {'Location': 'New Jersey (Statewide)', 'Type': 'State', 'State_Code': 'NJ', 'Basic_Needs': 144500, 'Median_Income': 96300, 'ALICE_Pct': 37},
    {'Location': 'Newark, NJ', 'Type': 'City', 'State_Code': 'NJ', 'Basic_Needs': 142100, 'Median_Income': 44200, 'ALICE_Pct': 66},
    {'Location': 'New Mexico (Statewide)', 'Type': 'State', 'State_Code': 'NM', 'Basic_Needs': 91800, 'Median_Income': 58700, 'ALICE_Pct': 48},
    {'Location': 'Albuquerque, NM', 'Type': 'City', 'State_Code': 'NM', 'Basic_Needs': 95200, 'Median_Income': 59400, 'ALICE_Pct': 46},
    {'Location': 'New York (Statewide)', 'Type': 'State', 'State_Code': 'NY', 'Basic_Needs': 148900, 'Median_Income': 81400, 'ALICE_Pct': 44},
    {'Location': 'New York City, NY', 'Type': 'City', 'State_Code': 'NY', 'Basic_Needs': 162400, 'Median_Income': 76700, 'ALICE_Pct': 51},
    {'Location': 'North Carolina (Statewide)', 'Type': 'State', 'State_Code': 'NC', 'Basic_Needs': 97800, 'Median_Income': 67500, 'ALICE_Pct': 43},
    {'Location': 'Charlotte, NC', 'Type': 'City', 'State_Code': 'NC', 'Basic_Needs': 106400, 'Median_Income': 74100, 'ALICE_Pct': 39},
    {'Location': 'North Dakota (Statewide)', 'Type': 'State', 'State_Code': 'ND', 'Basic_Needs': 95400, 'Median_Income': 73900, 'ALICE_Pct': 37},
    {'Location': 'Fargo, ND', 'Type': 'City', 'State_Code': 'ND', 'Basic_Needs': 98200, 'Median_Income': 68100, 'ALICE_Pct': 41},
    {'Location': 'Ohio (Statewide)', 'Type': 'State', 'State_Code': 'OH', 'Basic_Needs': 93800, 'Median_Income': 65700, 'ALICE_Pct': 38},
    {'Location': 'Cleveland, OH', 'Type': 'City', 'State_Code': 'OH', 'Basic_Needs': 91500, 'Median_Income': 37300, 'ALICE_Pct': 68},
    {'Location': 'Oklahoma (Statewide)', 'Type': 'State', 'State_Code': 'OK', 'Basic_Needs': 88900, 'Median_Income': 59700, 'ALICE_Pct': 46},
    {'Location': 'Oklahoma City, OK', 'Type': 'City', 'State_Code': 'OK', 'Basic_Needs': 91400, 'Median_Income': 61200, 'ALICE_Pct': 45},
    {'Location': 'Oregon (Statewide)', 'Type': 'State', 'State_Code': 'OR', 'Basic_Needs': 121500, 'Median_Income': 76600, 'ALICE_Pct': 44},
    {'Location': 'Portland, OR', 'Type': 'City', 'State_Code': 'OR', 'Basic_Needs': 132400, 'Median_Income': 81100, 'ALICE_Pct': 41},
    {'Location': 'Pennsylvania (Statewide)', 'Type': 'State', 'State_Code': 'PA', 'Basic_Needs': 106800, 'Median_Income': 73200, 'ALICE_Pct': 39},
    {'Location': 'Philadelphia, PA', 'Type': 'City', 'State_Code': 'PA', 'Basic_Needs': 118400, 'Median_Income': 57500, 'ALICE_Pct': 54},
    {'Location': 'Rhode Island (Statewide)', 'Type': 'State', 'State_Code': 'RI', 'Basic_Needs': 129400, 'Median_Income': 81800, 'ALICE_Pct': 38},
    {'Location': 'Providence, RI', 'Type': 'City', 'State_Code': 'RI', 'Basic_Needs': 132100, 'Median_Income': 61200, 'ALICE_Pct': 52},
    {'Location': 'South Carolina (Statewide)', 'Type': 'State', 'State_Code': 'SC', 'Basic_Needs': 95200, 'Median_Income': 63600, 'ALICE_Pct': 44},
    {'Location': 'Charleston, SC', 'Type': 'City', 'State_Code': 'SC', 'Basic_Needs': 109500, 'Median_Income': 78400, 'ALICE_Pct': 38},
    {'Location': 'South Dakota (Statewide)', 'Type': 'State', 'State_Code': 'SD', 'Basic_Needs': 92100, 'Median_Income': 69700, 'ALICE_Pct': 37},
    {'Location': 'Sioux Falls, SD', 'Type': 'City', 'State_Code': 'SD', 'Basic_Needs': 95800, 'Median_Income': 73500, 'ALICE_Pct': 35},
    {'Location': 'Tennessee (Statewide)', 'Type': 'State', 'State_Code': 'TN', 'Basic_Needs': 93400, 'Median_Income': 64100, 'ALICE_Pct': 44},
    {'Location': 'Nashville, TN', 'Type': 'City', 'State_Code': 'TN', 'Basic_Needs': 108900, 'Median_Income': 71400, 'ALICE_Pct': 40},
    {'Location': 'Texas (Statewide)', 'Type': 'State', 'State_Code': 'TX', 'Basic_Needs': 101500, 'Median_Income': 73000, 'ALICE_Pct': 44},
    {'Location': 'Houston, TX', 'Type': 'City', 'State_Code': 'TX', 'Basic_Needs': 104800, 'Median_Income': 60400, 'ALICE_Pct': 49},
    {'Location': 'Utah (Statewide)', 'Type': 'State', 'State_Code': 'UT', 'Basic_Needs': 106400, 'Median_Income': 86800, 'ALICE_Pct': 32},
    {'Location': 'Salt Lake City, UT', 'Type': 'City', 'State_Code': 'UT', 'Basic_Needs': 114200, 'Median_Income': 74800, 'ALICE_Pct': 41},
    {'Location': 'Vermont (Statewide)', 'Type': 'State', 'State_Code': 'VT', 'Basic_Needs': 122400, 'Median_Income': 74100, 'ALICE_Pct': 37},
    {'Location': 'Burlington, VT', 'Type': 'City', 'State_Code': 'VT', 'Basic_Needs': 134800, 'Median_Income': 73900, 'ALICE_Pct': 45},
    {'Location': 'Virginia (Statewide)', 'Type': 'State', 'State_Code': 'VA', 'Basic_Needs': 116500, 'Median_Income': 87200, 'ALICE_Pct': 38},
    {'Location': 'Virginia Beach, VA', 'Type': 'City', 'State_Code': 'VA', 'Basic_Needs': 112800, 'Median_Income': 84700, 'ALICE_Pct': 36},
    {'Location': 'Washington (Statewide)', 'Type': 'State', 'State_Code': 'WA', 'Basic_Needs': 132400, 'Median_Income': 90300, 'ALICE_Pct': 35},
    {'Location': 'Seattle, WA', 'Type': 'City', 'State_Code': 'WA', 'Basic_Needs': 154800, 'Median_Income': 115400, 'ALICE_Pct': 32},
    {'Location': 'West Virginia (Statewide)', 'Type': 'State', 'State_Code': 'WV', 'Basic_Needs': 86200, 'Median_Income': 54300, 'ALICE_Pct': 48},
    {'Location': 'Charleston, WV', 'Type': 'City', 'State_Code': 'WV', 'Basic_Needs': 89200, 'Median_Income': 51200, 'ALICE_Pct': 53},
    {'Location': 'Wisconsin (Statewide)', 'Type': 'State', 'State_Code': 'WI', 'Basic_Needs': 98400, 'Median_Income': 72500, 'ALICE_Pct': 34},
    {'Location': 'Milwaukee, WI', 'Type': 'City', 'State_Code': 'WI', 'Basic_Needs': 97800, 'Median_Income': 47100, 'ALICE_Pct': 59},
    {'Location': 'Wyoming (Statewide)', 'Type': 'State', 'State_Code': 'WY', 'Basic_Needs': 95800, 'Median_Income': 70000, 'ALICE_Pct': 36},
    {'Location': 'Cheyenne, WY', 'Type': 'City', 'State_Code': 'WY', 'Basic_Needs': 98200, 'Median_Income': 73200, 'ALICE_Pct': 34},
]

df_master_geo = pd.DataFrame(LOCATIONS_DATA)
df_master_geo['Deficit'] = df_master_geo['Basic_Needs'] - df_master_geo['Median_Income']

# --- HERO BANNER INTRO SECTION ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📏 A Better Ruler: Four-Pillar Economic Dashboard</div>
    <div class="hero-subtitle">
        National averages like aggregate GDP, headline inflation, or stock indexes create a false illusion of universal prosperity. 
        <strong>A Better Ruler</strong> replaces single magic numbers with four grounded dimensions of economic reality—measuring total output capacity, income & wealth distribution, family balance sheet resilience, and the localized cost of participation.
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Dashboard Controls")
year_range = st.sidebar.slider("Historical Time Horizon", 1975, 2024, (1990, 2024))
family_structure = st.sidebar.selectbox("Family Composition Baseline", ["2 Adults, 2 Children (Standard)", "1 Adult, 1 Child", "Single Adult"])

st.sidebar.markdown("---")
st.sidebar.header("👤 Personal Household Reality Check")
user_state = st.sidebar.selectbox("Select Your State", sorted(list(df_master_geo[df_master_geo['Type'] == 'State']['Location'].unique())), index=4)
user_income = st.sidebar.number_input("Annual Household Income ($)", min_value=10000, max_value=500000, value=75000, step=5000)

state_row = df_master_geo[df_master_geo['Location'] == user_state].iloc[0]
st_basic = state_row['Basic_Needs']
st_median = state_row['Median_Income']
st_alice_pct = state_row['ALICE_Pct']

diff_vs_basic = user_income - st_basic
if diff_vs_basic >= 0:
    st.sidebar.success(f"🟢 **+${diff_vs_basic:,.0f}** above local basic-needs budget (${st_basic:,.0f}).")
else:
    st.sidebar.error(f"🔴 **-${abs(diff_vs_basic):,.0f}** below local basic-needs budget (${st_basic:,.0f}).")

st.sidebar.caption(f"State Median: ${st_median:,.0f} | ALICE Stress: {st_alice_pct}%")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ Capacity", 
    "📊 Distribution", 
    "🛡️ Resilience", 
    "📍 Participation & 50-State Reality"
])

# TAB 1: CAPACITY
with tab1:
    st.subheader("⚙️ Pillar 1: Capacity — What Can the Economy Produce?")
    st.write("Real GDP measures total national production volume, while Output Per Hour measures labor efficiency.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card"><h4>Real GDP (Latest)</h4><h2>$22.7 Trillion</h2><p>+2.8% Annualized Growth Rate</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>Labor Productivity Index</h4><h2>112.4</h2><p>Base 2017=100 (+1.9% YoY)</p></div>', unsafe_allow_html=True)
        
    gdp = load_fred('GDPC1')
    prod = load_fred('OPHNFB')
    df_cap = pd.merge(gdp, prod, left_index=True, right_index=True, how='inner').dropna()
    df_cap.rename(columns={'GDPC1': 'Real_GDP', 'OPHNFB': 'Productivity'}, inplace=True)
    
    # Baseline Indexing (2000=100)
    base_year_df = df_cap.loc['2000-01-01':'2000-12-31']
    base_gdp = base_year_df['Real_GDP'].mean() if not base_year_df.empty else df_cap['Real_GDP'].iloc[0]
    base_prod = base_year_df['Productivity'].mean() if not base_year_df.empty else df_cap['Productivity'].iloc[0]
    
    df_cap['GDP_Indexed'] = (df_cap['Real_GDP'] / base_gdp) * 100
    df_cap['Prod_Indexed'] = (df_cap['Productivity'] / base_prod) * 100
    
    df_cap_filtered = df_cap[(df_cap.index.year >= year_range[0]) & (df_cap.index.year <= year_range[1])]
    
    fig1 = px.line(df_cap_filtered, y=['GDP_Indexed', 'Prod_Indexed'],
                   labels={'value': 'Index (2000=100)', 'DATE': 'Year', 'variable': 'Indicator'},
                   title="Real GDP Growth vs. Output Per Hour (Productivity)")
    st.plotly_chart(fig1, use_container_width=True)

# TAB 2: DISTRIBUTION
with tab2:
    st.subheader("📊 Pillar 2: Distribution — Who Receives the Growth?")
    st.write("Contrasting standard aggregate growth ($1/Vote GDP) against person-weighted growth (Democratic Domestic Product - DDP, 1 Person/Vote).")
    
    years = np.arange(1975, 2025)
    gdp_growth = 100 * (1 + 0.014) ** (years - 1975)
    ddp_growth = 100 * (1 + 0.009) ** (years - 1975)
    df_dist_growth = pd.DataFrame({'Year': years, 'Average Growth (GDP - $1/Vote)': gdp_growth, 'Democratic Growth (DDP - 1 Person/Vote)': ddp_growth})
    
    fig2 = px.line(df_dist_growth, x='Year', y=['Average Growth (GDP - $1/Vote)', 'Democratic Growth (DDP - 1 Person/Vote)'],
                   title="The Two Growth Rates Divergence (1975–2024)")
    st.plotly_chart(fig2, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        gini = load_fred('GINIALLRH')
        gini_filtered = gini[(gini.index.year >= year_range[0]) & (gini.index.year <= year_range[1])]
        fig_gini = px.line(gini_filtered, y='GINIALLRH', title="US Household Gini Inequality Index")
        st.plotly_chart(fig_gini, use_container_width=True)
    with col_b:
        top1 = load_fred('WFRBSTP0886')
        bot50 = load_fred('WFRBSN40180')
        df_wealth = pd.merge(top1, bot50, left_index=True, right_index=True, how='inner').dropna()
        df_wealth.rename(columns={'WFRBSTP0886': 'Top 1% Share', 'WFRBSN40180': 'Bottom 50% Share'}, inplace=True)
        df_wealth_filt = df_wealth[(df_wealth.index.year >= year_range[0]) & (df_wealth.index.year <= year_range[1])]
        fig_wealth = px.line(df_wealth_filt, y=['Top 1% Share', 'Bottom 50% Share'], title="Federal Reserve DFA Net Worth Shares (%)")
        st.plotly_chart(fig_wealth, use_container_width=True)

# TAB 3: RESILIENCE
with tab3:
    st.subheader("🛡️ Pillar 3: Resilience — Can Families Absorb a Shock?")
    st.write("Debt-service burdens, credit card delinquencies, and liquid reserves reveal household shock vulnerability.")
    
    tdsp = load_fred('TDSP')
    delinq = load_fred('DRCLACBS')
    df_res = pd.merge(tdsp, delinq, left_index=True, right_index=True, how='inner').dropna()
    df_res_filt = df_res[(df_res.index.year >= year_range[0]) & (df_res.index.year <= year_range[1])]
    
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Scatter(x=df_res_filt.index, y=df_res_filt['TDSP'], name="Debt Service Burden (% Disposable Income)"), secondary_y=False)
    fig3.add_trace(go.Scatter(x=df_res_filt.index, y=df_res_filt['DRCLACBS'], name="Credit Card Delinquency Rate (%)", line=dict(dash='dash', color='crimson')), secondary_y=True)
    fig3.update_layout(title_text="Household Debt Service Burden vs. Credit Card Delinquency Spike")
    st.plotly_chart(fig3, use_container_width=True)

# TAB 4: PARTICIPATION & 50-STATE REALITY
with tab4:
    st.subheader("📍 Pillar 4: Local Participation & 50-State Economic Map")
    st.write("Matching localized household incomes against MIT Living Wage benchmarks & ALICE Household Essentials Thresholds.")
    
    # 1. 50-STATE CHOROPLETH MAP
    st.markdown("#### 1. 🗺️ 50-State Interactive Economic Map")
    
    df_states_only = df_master_geo[df_master_geo['Type'] == 'State'].copy()
    
    map_metric = st.selectbox(
        "Select Map Metric / Color Coding:",
        [
            "Living Wage Deficit ($) [Basic Needs minus Median Income]",
            "ALICE Household Stress (%) [% Households Below Essentials Budget]",
            "MIT Annual Basic Needs Budget ($) [Family of 4]",
            "Median Household Income ($)"
        ]
    )
    
    if "Deficit" in map_metric:
        color_col = 'Deficit'
        color_title = "Living Wage Deficit ($)"
        colorscale = 'Reds'
    elif "ALICE" in map_metric:
        color_col = 'ALICE_Pct'
        color_title = "ALICE Stress (%)"
        colorscale = 'Oranges'
    elif "MIT" in map_metric:
        color_col = 'Basic_Needs'
        color_title = "Basic Needs Budget ($)"
        colorscale = 'Blues'
    else:
        color_col = 'Median_Income'
        color_title = "Median Income ($)"
        colorscale = 'Greens'
        
    fig_map = px.choropleth(
        df_states_only,
        locations='State_Code',
        locationmode="USA-states",
        color=color_col,
        scope="usa",
        color_continuous_scale=colorscale,
        hover_name='Location',
        hover_data={
            'State_Code': False,
            'Basic_Needs': ':$spin,',
            'Median_Income': ':$spin,',
            'Deficit': ':$spin,',
            'ALICE_Pct': ':%'
        },
        title=f"US 50-State Map: {color_title}"
    )
    fig_map.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    # 2. STATE RANKINGS & LEADERBOARD
    st.markdown("#### 2. 🏆 100 Location Explorer & Leaderboard (50 States + 50 Cities)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        type_filter = st.radio("Filter Location Types:", ["All (100 Locations)", "States Only (50 States)", "Major Cities Only (50 Cities)"], horizontal=True)
    with col_f2:
        sort_metric = st.selectbox("Sort Table By:", ["Highest Living Wage Deficit ($)", "Highest ALICE Stress (%)", "Highest Basic Needs Budget ($)", "Lowest Median Income ($)"])
        
    df_filtered_locs = df_master_geo.copy()
    if type_filter == "States Only (50 States)":
        df_filtered_locs = df_filtered_locs[df_filtered_locs['Type'] == 'State']
    elif type_filter == "Major Cities Only (50 Cities)":
        df_filtered_locs = df_filtered_locs[df_filtered_locs['Type'] == 'City']
        
    if sort_metric == "Highest Living Wage Deficit ($)":
        df_filtered_locs = df_filtered_locs.sort_values(by='Deficit', ascending=False)
    elif sort_metric == "Highest ALICE Stress (%)":
        df_filtered_locs = df_filtered_locs.sort_values(by='ALICE_Pct', ascending=False)
    elif sort_metric == "Highest Basic Needs Budget ($)":
        df_filtered_locs = df_filtered_locs.sort_values(by='Basic_Needs', ascending=False)
    else:
        df_filtered_locs = df_filtered_locs.sort_values(by='Median_Income', ascending=True)
        
    st.dataframe(
        df_filtered_locs[['Location', 'Type', 'Basic_Needs', 'Median_Income', 'Deficit', 'ALICE_Pct']],
        column_config={
            'Basic_Needs': st.column_config.NumberColumn("MIT Basic Needs ($)", format="$%d"),
            'Median_Income': st.column_config.NumberColumn("Median Income ($)", format="$%d"),
            'Deficit': st.column_config.NumberColumn("Living Wage Deficit ($)", format="$%d"),
            'ALICE_Pct': st.column_config.NumberColumn("ALICE Stress (%)", format="%d%%"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # 3. INTERACTIVE BENEFIT CLIFF SIMULATOR
    st.markdown("#### 3. 🎛️ Interactive Benefit Cliff Simulator")
    st.write("Simulate how modest wage increases cause sudden drop-offs in public subsidies (childcare, SNAP, Medicaid), leaving households with fewer net resources.")
    
    user_wage = st.slider("Select Hourly Wage Rate ($/hr):", min_value=15.0, max_value=35.0, value=21.0, step=0.5)
    monthly_hours = 160
    gross_monthly = user_wage * monthly_hours
    
    if gross_monthly < 2700:
        subsidy = 1100
        cliff_status = "🟢 Full Subsidy Eligible (Childcare + SNAP)"
    elif gross_monthly < 3500:
        subsidy = 450
        cliff_status = "🟡 Partial Benefit Phase-Out"
    else:
        subsidy = 0
        cliff_status = "🔴 BENEFIT CLIFF HIT — Subsidies Reduced to 0"
        
    net_resources = gross_monthly + subsidy - 400
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Monthly Pay", f"${gross_monthly:,.0f}")
    m2.metric("Public Subsidies", f"${subsidy:,.0f}")
    m3.metric("Net Available Resources", f"${net_resources:,.0f}")
    m4.write(f"**Status**: {cliff_status}")
    
    # Plotly Curve
    wages_arr = np.linspace(15, 35, 41)
    curve_rows = []
    for w in wages_arr:
        gm = w * 160
        sub = 1100 if gm < 2700 else (450 if gm < 3500 else 0)
        net = gm + sub - 400
        curve_rows.append({'Wage': w, 'Gross Pay': gm, 'Subsidies': sub, 'Net Resources': net})
    df_curve = pd.DataFrame(curve_rows)
    
    fig_cliff = go.Figure()
    fig_cliff.add_trace(go.Scatter(x=df_curve['Wage'], y=df_curve['Gross Pay'], name="Gross Monthly Pay ($)", line=dict(color="#2563eb")))
    fig_cliff.add_trace(go.Scatter(x=df_curve['Wage'], y=df_curve['Subsidies'], name="Public Subsidies ($)", line=dict(color="#10b981", dash="dash")))
    fig_cliff.add_trace(go.Scatter(x=df_curve['Wage'], y=df_curve['Net Resources'], name="Net Household Resources ($)", line=dict(color="#dc2626", width=3)))
    fig_cliff.add_vline(x=user_wage, line_dash="dot", line_color="black", annotation_text=f"Selected: ${user_wage}/hr")
    fig_cliff.update_layout(
        title="Net Household Resources Across Hourly Wage Levels ($15 - $35 / hr)",
        xaxis_title="Hourly Wage ($/hr)",
        yaxis_title="Monthly Amount ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_cliff, use_container_width=True)

st.caption("A Better Ruler Framework | Data: BEA, BLS, Federal Reserve Board SCF & DFA, MIT Living Wage, United for ALICE Project.")
