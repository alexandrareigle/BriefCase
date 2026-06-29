import yfinance as yf
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import anthropic
from email_sender import send_briefing_email
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#Loading API keys
load_dotenv()
newsapi=NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
claude=anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#-----MARKET DATA---------------------------------------------------------------------------
def get_stock_data(ticker):
    try:
        stock=yf.Ticker(ticker)
        hist=stock.history(period="5d")

        if hist.empty or len(hist)<2:
            return f"{ticker}: Data unavailable"

        today_close=hist["Close"].iloc[-1]
        yesterday_close=hist["Close"].iloc[-2]
        change=today_close-yesterday_close
        percent_change=(change/yesterday_close)*100
        direction ="UP" if change>0 else "DOWN"

        return f"{ticker}: ${today_close:.2f} | {direction} {abs(percent_change):.2f}% change"
    except Exception as e:
        return f"{ticker}: Data unavailable"

def get_market_summary(holdings):
    lines=[]

    lines.append("MAJOR INDEXES:")
    lines.append(get_stock_data("SPY"))
    lines.append(get_stock_data("QQQ"))
    lines.append(get_stock_data("DIA"))

    lines.append("\nFUTURES:")
    lines.append(get_stock_data("ES=F"))
    lines.append(get_stock_data("NQ=F"))

    lines.append("\nADVISOR HOLDINGS:")
    for ticker in holdings:
        lines.append(get_stock_data(ticker))

    return "\n".join(lines)

#----------EARNINGS CALENDAR---------------------------------------------------------------------------
def get_earnings_calendar(holdings):
    lines=[]
    lines.append("UPCOMING EARNINGS:")

    has_earnings=False

    for ticker in holdings:
        stock=yf.Ticker(ticker)
        try:
            calendar=stock.calendar
            if calendar is not None and not calendar.empty:
                earnings_date=calendar.index[0]
                lines.append(f" {ticker}: Earnings on {earnings_date.strftime('%B %d, %Y')}")
                has_earnings=True
        except:
            pass

    if not has_earnings:
        lines.append(" No upcoming earnings found for current holdings")

    return "\n".join(lines)

#------NEWS-------------------------------------------------------------------------------------
def get_news(topics):
    lines=[]
    for topic in topics:
        articles=newsapi.get_everything(
            q=topic,
            language="en",
            sort_by="publishedAt",
            page_size=3
        )
        lines.append(f"\n{topic}:")
        for article in articles["articles"]:
            lines.append(f" -  {article['title']} ({article['source']['name']})")
    return "\n".join(lines)

#----------PRICE ALERTS----------------------------------------------------------------------------------
def get_price_alerts(holdings,threshold=3.0):
    lines=[]
    alerts=[]

    for ticker in holdings:
        stock=yf.Ticker(ticker)
        hist=stock.history(period="5d")

        if len(hist)<2:
            continue

        today=hist["Close"].iloc[-1]
        yesterday=hist["Close"].iloc[-2]
        percent_change=((today-yesterday)/yesterday)*100

        if abs(percent_change) >= threshold:
            direction = "🛑 DOWN" if percent_change <0 else "🟢 UP"
            alerts.append(f" {ticker}: {direction} {abs(percent_change):.2f}% - SIGNIFICANT MOVE")

    if alerts:
        lines.append("⚠️ PRICE ALERTS - SIGNIFICANT MOVES OVERNIGHT:")
        lines.extend(alerts)
    else:
        lines.append("✅ NO PRICE ALERTS - No holdings moved more than 3% overnight")

    return "\n".join(lines)

#----------MACRO ECONOMIC DATA--------------------------------------------------------------------------------
def get_macro_data():
    lines=[]
    lines.append("MACRO ECONOMIC INDICATORS:")

    macro_tickers={
        "10-Year Treasury Yield": "^TNX",
        "20-Year Treasury Yield": "^TYX",
        "S&P 500 YTD": "^GSPC",
        "VIX (Volatility Index)": "^VIX",
        "Gold": "GC=F",
        "Crude Oil": "CL=F",
        "US Dollar Index": "DX-Y.NYB"
    }

    for name, ticker in macro_tickers.items():
        try:
            stock=yf.Ticker(ticker)
            hist=stock.history(period="1mo")

            print(f'DEBUG {ticker}: rows={len(hist)}, empty={hist.empty}')

            if len(hist)<2:
                lines.append(f" {name}: Data unavailable")
                continue

            today=hist["Close"].iloc[-1]
            yesterday=hist["Close"].iloc[-2]
            change=((today-yesterday)/yesterday)*100
            direction="🟢" if change >0 else "🛑"

            #Special formatting for yields (show as %)
            if "Yield" in name:
                lines.append(f" {direction} {name}: {today:.2f}% ({change:+.2f}%")
            else:
                lines.append(f" {direction} {name}: {today:.2f} ({change:+.2f}%")
        except Exception as e:
            print(f'DEBUG ERROR {ticker}: {str(e)}')
            lines.append(f" {name}: Data unavailable")

    return "\n".join(lines)

#----------SECTOR PERFORMANCE----------------------------------------------------------------------------------
def get_sector_performance():
    sectors= {
        "Technology":   "XLK",
        "Healthcare":   "XLV",
        "Financials":   "XLF",
        "Energy":   "XLE",
        "Consumer Staples": "XLP",
        "Industrials":  "XLI",
        "Real Estate":  "XLRE",
        "Utilities":    "XLU",
        "Materials":    "XLB",
        "Communication":    "XLC" }

    lines=[]
    lines.append("SECTOR PERFORMANCE")

    for sector_name, ticker in sectors.items():
        stock=yf.Ticker(ticker)
        hist=stock.history(period="5d")

        if len(hist)<2:
            lines.append(f"  ⚠️{sector_name} Data unavailable")
            continue

        today=hist["Close"].iloc[-1]
        yesterday=hist["Close"].iloc[-2]
        percent_change=((today-yesterday)/yesterday)*100
        direction="🟢" if percent_change >0 else "🛑"

        lines.append(f" {direction} {sector_name}: {percent_change:.2f}%")

    return "\n".join(lines)


#--------CLAUDE NEWSLETTER WRITER--------------------------------------------------------------------
def generate_newsletter(advisor, market_data, news, earnings, alerts, macro, sectors):
    prompt = f"""You are BriefCase, an elite AI morning intelligence assistant build exclusively for financial advisors at Cary Street Partners, a wealth management firm.

Your job is to deliver world-class personalized morning briefing that saves advisors 1-2 hours of research every single morning and prepares them for every client conversation of the day.

ADVISOR PROFILE: 
- Name: {advisor['name']}
- Risk Profile: {advisor['risk_profile']}
- Focus Areas: {', '.join(advisor['topics'])}

MARKET DATA
{market_data}

LATEST NEWS:
{news}

UPCOMING EARNINGS FOR HOLDINGS (YOU MUST INCLUDE THIS AS ITS OWN SECTION):
{earnings}

PRICE ALERTS (YOU MUST INCLUDE THIS):
{alerts}

MACRO ECONOMIC INDICATORS (INCLUDE AS ITS OWN SECTION):
{macro}

SECTOR PERFORMANCE DATA (YOU MUST INCLUDE THIS AS ITS OWN SECTION:
{sectors}

Write a morning briefing with these exact sections. Be concise - use bullet points, no long paragraphs:

---
☀️ Good Morning, {advisor['name']}
One sentence market tone.

---
📊 Market Snapshot
3 bullet points: future direction, index performance, market sentiment

---
💼 Your Holdings - What Moved & Why
One bullet point per holding: ticker, price, % change, one sentence why if move >1%

---
📰 Key News
3 bullets max: headline, which holding it affects, one sentence takeaway

---
🗓️ EARNINGS WATCH 
Use EXACTLY the earnings data provided. One line per ticker

---
🌍MACRO ECONOMIC INDICATORS
One line per indicator from the macro data provided. Show the value and direction

---
📊 SECTOR PERFORMANCE 
use EXACTLY the sector data provided. One line per sector with % change

---
 ⚡ Action Items
3 bullet points, specific and direct.

Have a great day {advisor['name']}!

IMPORTANT RULES:
- Always use real numbers from the data provided
- Never make up price movements or news events
- If a holding had no significant news, say so briefly rather than fabricating a reason
- Keep the tone confident, professional, and warm - like a brilliant colleague, not a robot
- Format everything cleanly with headers, bullet points, and tables where appropriate
- Include a dedicated SECTOR PERFORMANCE section showing which sectors are up and down using the sector data provided
- Include EARNINGS WATCH section flagging any upcoming earnings from the holdings data provided
- Use bullet points throughout instead of long paragraphs - advisors need to scan quickly, not read essays
- Keep each section tight and scannable - no paragraph should be longer than 3 sentences
"""

    message=claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

#---------ADVISOR PROFILE------------------------------------------------------------------------------
advisor={
    "name": "Alexandra Reigle",
    "email": "alexandrareigle10@gmail.com",
    "risk_profile": "Moderate",
    "holdings": ["AAPL", "NVDA", "MSFT", "VTI","ORCL"],
    "topics": ["Federal Reserve", "NVIDIA", 'Apple Earnings']}

#------------RUN EVERYTHING------------------------------------------------------------------
import json

#LOAD ADVISORS FROM QUESTIONAIRE
def get_sheet():
    import json
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    #Try environment variable first (for cloud deployment)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict=json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        #Fall back to local file (for local development)
        creds_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "briefcase-credentials.json")
        creds=ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

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

#RUN EVERYTHING FOR EACH ADVISOR
advisors=load_advisors()

if not advisors:
    print("No advisors found in advisors.json. Please have advisors complete the questionaire first.")
else:
    for advisor in advisors:
        print(f"\nGenerating BriefCase morning briefing for {advisor['name']}...\n")

        market_data=get_market_summary(advisor["holdings"])
        news=get_news(advisor["topics"])
        earnings=get_earnings_calendar(advisor["holdings"])
        alerts=get_price_alerts(advisor["holdings"])
        macro=get_macro_data()
        sectors=get_sector_performance()

        print("Data pulled. Sending to Claude...\n")

        newsletter=generate_newsletter(advisor, market_data, news, earnings, alerts, macro, sectors)

        print("="*60)
        print(f'BRIEFCASE MORNING BRIEFING - {advisor['name']}')
        print("="*60)
        print(newsletter)
        print("="*60)

        send_briefing_email(
            advisor_name=f"{advisor["name"]} - {advisor.get('group_name', 'General')}",
            advisor_email=advisor["email"],
            briefing_content=newsletter
        )
        print(f"Briefing sent to {advisor['name']} at {advisor['email']}!\n")