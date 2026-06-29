import streamlit as st
import anthropic
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv()
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.set_page_config(
    page_title="Primer — Meeting Prep",
    page_icon="📋",
    layout="centered"
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
        max-width: 760px !important;
    }

    .stFormSubmitButton button {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }

    .stTextInput label, .stSelectbox label,
    .stMultiSelect label, .stTextArea label {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #374151 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stTextInput input, .stTextArea textarea {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FAFBFD !important;
    }

    .stSelectbox > div > div {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FAFBFD !important;
    }

    .output-section {
        background: white;
        border-radius: 12px;
        padding: 24px 28px;
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    .output-header {
        font-size: 11px;
        font-weight: 700;
        color: #2E5FA3;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-bottom: 8px;
        border-bottom: 2px solid #E8EFF8;
        margin-bottom: 16px;
    }

    .disclaimer {
        background: #FFF8E7;
        border: 1px solid #F59E0B;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 12px;
        color: #92400E;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
            padding: 28px 32px; border-radius: 12px; margin-bottom: 24px;">
    <div style="font-size: 28px; font-weight: 800; color: white; margin-bottom: 4px;">
        📋 Primer
    </div>
    <div style="color: #a0b4d0; font-size: 13px;">
        AI-Powered Meeting Prep · Cary Street Partners
    </div>
    <div style="color: #7a9cc7; font-size: 12px; margin-top: 6px;">
        Ask the right questions. Have the right conversation.
    </div>
</div>
""", unsafe_allow_html=True)

# ── FORM ───────────────────────────────────────────────────
with st.form("primer_form"):
    # Section 1: Meeting Details
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        01 · Meeting Details
    </div>
    """, unsafe_allow_html=True)

    meeting_type = st.selectbox(
        "Meeting Type",
        [
            "Quarterly Review",
            "Annual Review",
            "New Client Onboarding",
            "Market Volatility Check-in",
            "Retirement Planning",
            "Estate & Legacy Planning",
            "Major Life Event",
            "Tax Planning",
            "Portfolio Rebalancing",
            "General Check-in"
        ]
    )

    st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)

    # Section 2: Client Profile
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        02 · Client Profile
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        age_range = st.selectbox(
            "Client Age Range",
            ["30s", "40s", "50s", "60s", "70s+"]
        )
    with col2:
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"]
        )
    with col3:
        time_horizon = st.selectbox(
            "Time Horizon",
            ["Short (1-3 years)", "Medium (3-7 years)", "Long (7+ years)"]
        )

    st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)

    # Section 3: Holdings
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        03 · Holdings to Discuss
    </div>
    """, unsafe_allow_html=True)

    holdings_input = st.text_input(
        "Stock Tickers",
        placeholder="AAPL, NVDA, VTI, BRK-B"
    )
    st.caption("Enter the specific holdings you want to discuss in this meeting")

    st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)

    # Section 4: Context
    st.markdown("""
    <div style="font-size: 11px; font-weight: 700; color: #2E5FA3;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 16px; padding-bottom: 8px;
                border-bottom: 2px solid #E8EFF8;">
        04 · Client Context
    </div>
    """, unsafe_allow_html=True)

    recent_concerns = st.text_area(
        "Recent Concerns or Life Events",
        placeholder="e.g. Client mentioned concerns about inflation, recently retired, going through a divorce, expecting an inheritance...",
        height=100
    )

    specific_topics = st.text_area(
        "Specific Topics to Cover",
        placeholder="e.g. Discuss rebalancing tech exposure, review beneficiaries, talk about adding bonds...",
        height=80
    )

    st.markdown("<div style='margin-bottom: 8px'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "📋 Generate Meeting Prep",
        use_container_width=True
    )

# ── GENERATE PREP ──────────────────────────────────────────
if submitted:
    if not holdings_input:
        st.error("Please enter at least one holding to discuss.")
    else:
        holdings = [h.strip().upper() for h in holdings_input.split(",") if h.strip()]

        # Fetch live market data for holdings
        market_context = []
        for ticker in holdings:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty and len(hist) >= 2:
                    today = hist["Close"].iloc[-1]
                    yesterday = hist["Close"].iloc[-2]
                    change = ((today - yesterday) / yesterday) * 100
                    direction = "UP" if change > 0 else "DOWN"
                    market_context.append(f"{ticker}: ${today:.2f} | {direction} {abs(change):.2f}%")
                else:
                    market_context.append(f"{ticker}: Price data unavailable")
            except:
                market_context.append(f"{ticker}: Price data unavailable")

        market_data_str = "\n".join(market_context)

        with st.spinner("Generating your meeting prep..."):

            prompt = f"""You are Primer, an AI meeting preparation assistant for financial advisors at Cary Street Partners.

Your job is to help advisors have better, more meaningful conversations with their clients by generating smart questions and conversation frameworks — NOT investment recommendations or market predictions.

MEETING CONTEXT:
- Meeting Type: {meeting_type}
- Client Age Range: {age_range}
- Risk Tolerance: {risk_tolerance}
- Time Horizon: {time_horizon}
- Holdings to Discuss: {', '.join(holdings)}
- Recent Client Concerns/Life Events: {recent_concerns if recent_concerns else 'None provided'}
- Specific Topics to Cover: {specific_topics if specific_topics else 'None provided'}

CURRENT MARKET DATA FOR HOLDINGS:
{market_data_str}

Generate a comprehensive meeting prep package with the following sections. Focus entirely on questions and conversation frameworks — never make specific investment recommendations:

## 📋 Suggested Meeting Agenda
A clean 5-7 point agenda for this specific meeting type and client profile.

## 🎯 Key Objectives for This Meeting
3-4 bullet points on what a successful meeting looks like for this client.

## ❓ Questions the Client Will Likely Ask
5-6 questions this client is likely to raise based on their profile, the meeting type, and current market conditions. For each question provide a brief note on what the advisor should be ready to address — not a scripted answer, just the key points to hit.

## 🔍 Discovery Questions for the Advisor to Ask
8-10 thoughtful questions the advisor should ask to uncover the client's true needs, concerns, and any life changes. Organize by category:
- Financial situation questions
- Goals and priorities questions  
- Risk and emotions questions
- Life changes and planning questions

## 👂 What to Listen For
5 specific signals or phrases that suggest the client may need something different than what's currently planned — things that should prompt a follow up conversation or plan adjustment.

## 📄 Leave-Behind Agenda
A clean one-page agenda the advisor can print and bring to the meeting. Professional and client-friendly.

IMPORTANT RULES:
- Never make specific buy, sell, or hold recommendations
- Never predict market movements
- Frame everything as questions and conversation guides
- Keep tone warm, professional, and human
- Be specific to this client's profile and situation — not generic"""

            message = claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text

        # Display disclaimer
        st.markdown("""
        <div class="disclaimer">
            ⚠️ <strong>Advisor Use Only:</strong> Primer generates conversation frameworks to assist meeting preparation.
            This content is not for client distribution. All investment decisions remain the sole responsibility
            of the advisor. Verify all market data before use.
        </div>
        """, unsafe_allow_html=True)

        # Display results
        st.markdown(result)

        # Download button
        st.download_button(
            label="⬇️ Download Meeting Prep",
            data=result,
            file_name=f"primer_{meeting_type.replace(' ', '_').lower()}_prep.txt",
            mime="text/plain",
            use_container_width=True
        )
