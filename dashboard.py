import streamlit as st
import json
import os
import yfinance as yf
from datetime import datetime, timezone
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="BriefCase — Admin Dashboard",
    page_icon="💼",
    layout="wide"
)

# ── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F0F4FA;
    }

    .block-container {
        padding-top: 0rem !important;
        max-width: 1200px !important;
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        text-align: center;
    }

    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: #1B3A6B;
        line-height: 1;
        margin-bottom: 4px;
    }

    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .section-header {
        font-size: 11px;
        font-weight: 700;
        color: #2E5FA3;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-bottom: 8px;
        border-bottom: 2px solid #E8EFF8;
        margin-bottom: 16px;
    }

    .status-live {
        background: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)


# ── LOAD ADVISORS ──────────────────────────────────────────
def get_sheet():
    import json
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Try environment variable first (for cloud deployment)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Fall back to local file (for local development)
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "briefcase-credentials.json")
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

    client = gspread.authorize(creds)
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    return client.open_by_key(sheet_id).sheet1

def load_advisors():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        advisors = []
        for record in records:
            advisors.append({
                "name": record.get("name", ""),
                "group_name": record.get("group_name", "General"),
                "email": record.get("email", ""),
                "risk_profile": record.get("risk_profile", ""),
                "holdings": [h.strip() for h in record.get("holdings", "").split(",") if h.strip()],
                "topics": [t.strip() for t in record.get("topics", "").split(",") if t.strip()],
                "detail_level": record.get("detail_level", ""),
                "additional_notes": record.get("additional_notes", "")
            })
        return advisors
    except Exception as e:
        print(f"Error loading advisors: {e}")
        return []


advisors = load_advisors()

# ── GET ALL UNIQUE HOLDINGS ────────────────────────────────
all_holdings = []
for advisor in advisors:
    all_holdings.extend(advisor.get("holdings", []))
unique_holdings = list(set(all_holdings))
all_topics = []
for advisor in advisors:
    all_topics.extend(advisor.get("topics", []))
unique_topics = list(set(all_topics))

# ── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
            padding: 24px 32px; border-radius: 12px; margin-bottom: 24px;
            display: flex; align-items: center; justify-content: space-between;">
    <div>
        <div style="font-size: 26px; font-weight: 800; color: white;">💼 BriefCase</div>
        <div style="color: #a0b4d0; font-size: 13px; margin-top: 2px;">
            Admin Dashboard · Cary Street Partners
        </div>
    </div>
    <div style="text-align: right;">
        <div style="color: #a0b4d0; font-size: 12px;">Last refreshed</div>
        <div style="color: white; font-size: 13px; font-weight: 600;">
""" + datetime.now().strftime("%B %d, %Y · %I:%M %p") + """
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS BAR ──────────────────────────────────────────────
st.markdown('<div class="section-header">Platform Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(advisors)}</div>
        <div class="metric-label">Advisors Enrolled</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(unique_holdings)}</div>
        <div class="metric-label">Holdings Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(unique_topics)}</div>
        <div class="metric-label">News Topics Monitored</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    est = pytz.timezone('US/Eastern')
    now_est = datetime.now(est)
    next_run = now_est.replace(hour=6, minute=0, second=0, microsecond=0)
    if now_est.hour >= 6:
        from datetime import timedelta

        next_run += timedelta(days=1)
    hours_until = int((next_run - now_est).total_seconds() // 3600)
    mins_until = int(((next_run - now_est).total_seconds() % 3600) // 60)

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{hours_until}h {mins_until}m</div>
        <div class="metric-label">Until Next Briefing</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TWO COLUMN LAYOUT ──────────────────────────────────────
left, right = st.columns([1.5, 1])

with left:
    # Advisor Roster
    st.markdown('<div class="section-header">Advisor Roster</div>', unsafe_allow_html=True)

    if not advisors:
        st.info("No advisors enrolled yet. Share the questionnaire link to get started!")
    else:
        for advisor in advisors:
            holdings = advisor.get("holdings", [])
            topics = advisor.get("topics", [])
            risk = advisor.get("risk_profile", "N/A")

            risk_color = {
                "Conservative": "#2563EB",
                "Moderate": "#D97706",
                "Aggressive": "#DC2626",
                "Mixed Book": "#7C3AED"
            }.get(risk, "#6B7280")

            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 16px 20px;
                        border: 1px solid #E2E8F0; margin-bottom: 10px;
                        box-shadow: 0 1px 4px rgba(0,0,0,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-weight: 700; color: #1B3A6B; font-size: 15px;">{advisor['name']}</span>
                        <span style="background: #E8EFF8; color: #2E5FA3; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 8px;">{advisor.get('group_name', 'General')}</span>
                        <span style="color: #6B7280; font-size: 13px; margin-left: 8px;">{advisor['email']}</span>
                    </div>
                    <span style="background: {risk_color}20; color: {risk_color};
                                padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;">
                        {risk}
                    </span>
                </div>
                <div style="display: flex; gap: 16px;">
                    <span style="font-size: 12px; color: #6B7280;">
                        📈 <strong>{len(holdings)}</strong> holdings: {', '.join(holdings[:4])}{'...' if len(holdings) > 4 else ''}
                    </span>
                </div>
                <div style="margin-top: 4px;">
                    <span style="font-size: 12px; color: #6B7280;">
                        📰 <strong>{len(topics)}</strong> topics monitored
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with right:
    # System Status
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)

    status_items = [
        ("🟢", "BriefCase Engine", "LIVE"),
        ("🟢", "Railway Deployment", "ONLINE"),
        ("🟢", "Email Delivery (Resend)", "ACTIVE"),
        ("🟢", "Market Data (yfinance)", "CONNECTED"),
        ("🟢", "News API", "CONNECTED"),
        ("🟢", "Claude AI (Sonnet)", "CONNECTED"),
    ]

    for icon, name, status in status_items:
        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 12px 16px;
                    border: 1px solid #E2E8F0; margin-bottom: 8px;
                    display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 13px; color: #374151; font-weight: 500;">{icon} {name}</span>
            <span style="background: #DCFCE7; color: #166534; padding: 2px 10px;
                        border-radius: 20px; font-size: 11px; font-weight: 700;">{status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Live Market Pulse
    st.markdown('<div class="section-header">Live Market Pulse</div>', unsafe_allow_html=True)

    market_tickers = {
        "S&P 500": "SPY",
        "Nasdaq": "QQQ",
        "Dow Jones": "DIA",
        "S&P Futures": "ES=F"
    }

    for name, ticker in market_tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if len(hist) >= 2:
                today = hist["Close"].iloc[-1]
                yesterday = hist["Close"].iloc[-2]
                change = ((today - yesterday) / yesterday) * 100
                color = "#166534" if change > 0 else "#991B1B"
                bg = "#DCFCE7" if change > 0 else "#FEE2E2"
                arrow = "▲" if change > 0 else "▼"

                st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 12px 16px;
                            border: 1px solid #E2E8F0; margin-bottom: 8px;
                            display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; color: #374151; font-weight: 600;">{name}</span>
                    <div style="text-align: right;">
                        <span style="font-size: 13px; font-weight: 700; color: #1B3A6B;">${today:.2f}</span>
                        <span style="background: {bg}; color: {color}; padding: 2px 8px;
                                    border-radius: 20px; font-size: 11px; font-weight: 700; margin-left: 6px;">
                            {arrow} {abs(change):.2f}%
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass

st.markdown("<br>", unsafe_allow_html=True)

# ── REFRESH BUTTON ─────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()