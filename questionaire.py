import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="BriefCase — Advisor Onboarding",
    page_icon="💼",
    layout="centered"
)

# ── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Page background */
    .stApp {
        background-color: #F0F4FA;
    }

    /* Main container */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 720px !important;
    }

    /* Section cards */
    .section-card {
        background: white;
        border-radius: 12px;
        padding: 28px 32px;
        margin-bottom: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Section headers */
    .section-title {
        font-size: 15px;
        font-weight: 700;
        color: #1B3A6B;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
        padding-bottom: 10px;
        border-bottom: 2px solid #E8EFF8;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Step indicator */
    .step-badge {
        background: #1B3A6B;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
    }

    /* Input labels */
    .stTextInput label, .stSelectbox label,
    .stMultiSelect label, .stTextArea label {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #374151 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        color: #1B3A6B !important;
        background: #FAFBFD !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2E5FA3 !important;
        box-shadow: 0 0 0 3px rgba(46,95,163,0.1) !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FAFBFD !important;
    }

    /* Multiselect tags — override red with navy */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #1B3A6B !important;
        border-radius: 6px !important;
    }
    .stMultiSelect > div > div {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FAFBFD !important;
    }

    /* Submit button */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: opacity 0.2s !important;
    }
    .stFormSubmitButton button:hover {
        opacity: 0.92 !important;
    }

    /* Caption text */
    .stCaption {
        color: #6B7280 !important;
        font-size: 12px !important;
    }

    /* Divider */
    hr {
        border: none !important;
        border-top: 1px solid #E2E8F0 !important;
        margin: 20px 0 !important;
    }

    /* Success box */
    .success-card {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
        border-radius: 12px;
        padding: 32px;
        color: white;
        text-align: center;
        margin-top: 16px;
    }
    .success-card h2 {
        color: white;
        margin-bottom: 8px;
    }
    .success-detail {
        background: rgba(255,255,255,0.12);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


# ── LOAD/SAVE FUNCTIONS ────────────────────────────────────

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
        return records
    except:
        return []


def save_advisor(new_advisor):
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()

        # Check if advisor already exists
        for i, record in enumerate(records):
            if record.get("email") == new_advisor["email"] and record.get("group_name")==new_advisor["group_name"]:
                # Update existing row (row index is i+2 because of header)
                row_num = i + 2
                sheet.update(f"A{row_num}", [[
                    new_advisor["name"],
                    new_advisor.get("group_name", "General"),
                    new_advisor["email"],
                    new_advisor["risk_profile"],
                    ", ".join(new_advisor.get("investment_focus", [])),
                    ", ".join(new_advisor.get("holdings", [])),
                    ", ".join(new_advisor.get("topics", [])),
                    new_advisor.get("detail_level", ""),
                    new_advisor.get("additional_notes", "")
                ]])
                return "updated"

        # Add new advisor
        sheet.append_row([
            new_advisor["name"],
            new_advisor.get("group_name", "General"),
            new_advisor["email"],
            new_advisor["risk_profile"],
            ", ".join(new_advisor.get("investment_focus", [])),
            ", ".join(new_advisor.get("holdings", [])),
            ", ".join(new_advisor.get("topics", [])),
            new_advisor.get("detail_level", ""),
            new_advisor.get("additional_notes", "")
        ])
        return "created"
    except Exception as e:
        print(f"Error saving advisor: {e}")
        return "error"

# ── HEADER ─────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
            padding: 32px 36px; border-radius: 12px; margin-bottom: 24px;">
    <div style="font-size: 30px; font-weight: 800; color: white;
                letter-spacing: -0.5px; margin-bottom: 4px;">
        💼 BriefCase
    </div>
    <div style="color: #a0b4d0; font-size: 14px;">
        AI-Powered Morning Intelligence &nbsp;·&nbsp; Cary Street Partners
    </div>
</div>

<div style="margin-bottom: 28px;">
    <div style="font-size: 22px; font-weight: 700; color: #1B3A6B; margin-bottom: 6px;">
        Advisor Onboarding
    </div>
    <div style="font-size: 14px; color: #6B7280; line-height: 1.6;">
        Complete this form once. Every morning before the opening bell, BriefCase will deliver
        a personalized intelligence briefing directly to your inbox — built around your book of business.
    </div>
</div>
""", unsafe_allow_html=True)

# ── FORM ───────────────────────────────────────────────────

with st.form("advisor_form"):
    # Section 1: Personal Info
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        01 &nbsp;·&nbsp; Your Information
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="ex: Sarah Chen")
    with col2:
        email = st.text_input("Work Email", placeholder="ex: schen@carystreetpartners.com")

        group_name=st.text_input(
            "Briefing Group Name",
            placeholder="ex: Aggressive Clients, Conservative Clients, All Clients"
        )
        st.caption("Give this briefing a name so you can identify it. Create multiple briefings by submitting this form again with a different group name.")

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    # Section 2: Investment Profile
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        02 &nbsp;·&nbsp; Investment Profile
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        risk_profile = st.selectbox(
            "Primary Client Risk Profile",
            ["Conservative", "Moderate", "Aggressive", "Mixed Book"]
        )
    with col2:
        investment_focus = st.multiselect(
            "Investment Focus Areas",
            ["Growth", "Income", "Capital Preservation",
             "Balanced", "ESG / Sustainable",
             "Alternative Investments", "International"]
        )

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    # Section 3: Holdings
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        03 &nbsp;·&nbsp; Holdings to Track
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 13px; color: #6B7280; margin-bottom: 12px;">
        Enter the tickers you want monitored each morning, separated by commas.
        Supports all NYSE/NASDAQ listed stocks, ETFs, and funds.
    </div>
    """, unsafe_allow_html=True)

    holdings_input = st.text_input(
        "Stock Tickers",
        placeholder="AAPL, NVDA, MSFT, VTI, BRK-B"
    )

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    # Section 4: News Topics
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        04 &nbsp;·&nbsp; News & Market Intelligence
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        macro_topics = st.multiselect(
            "Macro & Economic Topics",
            ["Federal Reserve / Interest Rates", "Inflation / CPI",
             "Jobs Market", "GDP Growth", "Treasury Yields",
             "Dollar Strength", "Oil & Energy Prices",
             "China / Geopolitics", "Recession Risk"]
        )
    with col2:
        market_topics = st.multiselect(
            "Market & Sector Topics",
            ["Technology / AI", "Healthcare", "Financials / Banking",
             "Energy", "Consumer Spending", "Real Estate",
             "Earnings Season", "IPOs",
             "Crypto / Digital Assets", "ESG / Sustainability"]
        )

    custom_topics = st.text_input(
        "Additional Topics or Companies",
        placeholder="e.g. Apple earnings, Warren Buffett, semiconductors"
    )

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    # Section 5: Preferences
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        05 &nbsp;·&nbsp; Briefing Preferences
    </div>
    """, unsafe_allow_html=True)

    detail_level = st.selectbox(
            "Briefing Detail Level",
            ["Concise — key points only",
             "Standard — balanced detail",
             "Detailed — full analysis"]
        )

    additional_notes = st.text_area(
        "Anything else BriefCase should know?",
        placeholder="e.g. Several clients are heavily concentrated in tech, I have retirees focused on dividend income...",
        height=100
    )

    st.markdown("<div style='margin-bottom: 8px'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "🚀 Activate My BriefCase",
        use_container_width=True
    )

# ── HANDLE SUBMISSION ──────────────────────────────────────

if submitted:
    if not name or not email or not holdings_input:
        st.error("Please fill in your name, email, and at least one stock ticker.")
    else:
        holdings = [h.strip().upper() for h in holdings_input.split(",") if h.strip()]
        all_topics = macro_topics + market_topics
        if custom_topics:
            all_topics.extend([t.strip() for t in custom_topics.split(",")])

        advisor_profile = {
            "name": name,
            "group_name": group_name,
            "email": email,
            "risk_profile": risk_profile,
            "investment_focus": investment_focus,
            "holdings": holdings,
            "topics": all_topics,
            "detail_level": detail_level,
            "additional_notes": additional_notes
        }

        result = save_advisor(advisor_profile)

        st.markdown(f"""
        <div class="success-card">
            <div style="font-size: 32px; margin-bottom: 12px;">✅</div>
            <div style="font-size: 20px; font-weight: 700; margin-bottom: 6px;">
                Welcome to BriefCase, {name}!
            </div>
            <div style="color: #a0b4d0; font-size: 14px; margin-bottom: 20px;">
                Your personalized morning briefing is set up and ready to go.
            </div>
            <div class="success-detail">
                📧 &nbsp; Delivering to &nbsp;<strong style="color:white">{email}</strong>
            </div>
            <div class="success-detail">
                📈 &nbsp; Tracking &nbsp;<strong style="color:white">{len(holdings)} holdings</strong>
                &nbsp;—&nbsp; {', '.join(holdings)}
            </div>
            <div class="success-detail">
                📰 &nbsp; Monitoring &nbsp;<strong style="color:white">{len(all_topics)} news topics</strong>
            </div>
            <div style="color: #a0b4d0; font-size: 12px; margin-top: 16px;">
                Need to update your preferences? Fill out the form again with the same email address.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()