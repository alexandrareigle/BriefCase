import resend
import re
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def convert_markdown_to_html(text):
    # Convert headers
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Convert bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # Convert italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

    # Convert horizontal rules
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)

    # Convert blockquotes
    text = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # Convert bullet points and tables
    lines = text.split('\n')
    html_lines = []
    in_list = False
    in_table = False
    table_rows = []

    for line in lines:
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
            continue
        elif in_table:
            in_table = False
            html_lines.append(build_table(table_rows))
            table_rows = []

        if line.strip().startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(line)

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append(build_table(table_rows))

    text = '\n'.join(html_lines)

    paragraphs = text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<'):
            result.append(p)
        else:
            result.append(f'<p>{p}</p>')

    return '\n'.join(result)


def build_table(rows):
    html = '<table>'
    for i, row in enumerate(rows):
        if re.match(r'^\|[-| :]+\|$', row.strip()):
            continue
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        if i == 0:
            html += '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead><tbody>'
        else:
            html += '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
    html += '</tbody></table>'
    return html


def send_briefing_email(advisor_name, advisor_email, briefing_content):
    body_html = convert_markdown_to_html(briefing_content)

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    margin: 0;
    padding: 0;
    background-color: #F0F2F5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  }}
  .wrapper {{
    max-width: 680px;
    margin: 0 auto;
    padding: 24px 16px;
  }}
  .header {{
    background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
    border-radius: 12px 12px 0 0;
    padding: 28px 32px;
  }}
  .header-logo {{
    font-size: 26px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
  }}
  .header-sub {{
    color: #a0b4d0;
    font-size: 13px;
    margin-top: 4px;
  }}
  .header-date {{
    color: #7a9cc7;
    font-size: 12px;
    margin-top: 8px;
  }}
  .body {{
    background: #ffffff;
    padding: 32px;
    border-left: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    color: #1B3A6B;
    margin: 0 0 8px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #E2E8F0;
  }}
  h2 {{
    font-size: 15px;
    font-weight: 700;
    color: #1B3A6B;
    margin: 28px 0 12px 0;
    padding: 8px 12px;
    background: #F0F4FA;
    border-left: 3px solid #2E5FA3;
    border-radius: 0 6px 6px 0;
  }}
  p {{
    font-size: 14px;
    line-height: 1.7;
    color: #374151;
    margin: 0 0 12px 0;
  }}
  ul {{
    margin: 8px 0 16px 0;
    padding-left: 20px;
  }}
  li {{
    font-size: 14px;
    line-height: 1.7;
    color: #374151;
    margin-bottom: 8px;
  }}
  strong {{
    color: #1B3A6B;
    font-weight: 600;
  }}
  em {{
    color: #6B7280;
    font-style: italic;
  }}
  hr {{
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 20px 0;
  }}
  blockquote {{
    background: #FFF8E7;
    border-left: 3px solid #F59E0B;
    margin: 12px 0;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #92400E;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 20px 0;
    font-size: 13px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}
  thead {{
    background: #1B3A6B;
  }}
  th {{
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: white;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  td {{
    padding: 10px 14px;
    border-bottom: 1px solid #E2E8F0;
    color: #374151;
  }}
  tr:nth-child(even) td {{
    background: #F8FAFC;
  }}
  tr:last-child td {{
    border-bottom: none;
  }}
  .footer {{
    background: #1B3A6B;
    border-radius: 0 0 12px 12px;
    padding: 20px 32px;
    text-align: center;
  }}
  .footer p {{
    color: #7a9cc7;
    font-size: 11px;
    margin: 0;
  }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="header-logo">💼 BriefCase</div>
    <div class="header-sub">AI-Powered Morning Intelligence &nbsp;|&nbsp; Cary Street Partners</div>
    <div class="header-date">Morning Briefing for {advisor_name}</div>
  </div>
  <div class="body">
    {body_html}
  </div>
  <div class="footer">
    <p>BriefCase by Cary Street Partners &nbsp;|&nbsp; Not financial advice &nbsp;|&nbsp; Data reflects latest available market information</p>
  </div>
</div>
</body>
</html>
"""

    try:
        print(f"Sending email via Resend to {advisor_email}...")
        params = {
            "from": "BriefCase <onboarding@resend.dev>",
            "to": [advisor_email],
            "subject": f"☀️ BriefCase Morning Briefing — {advisor_name}",
            "html": html_content,
        }
        email = resend.Emails.send(params)
        print(f"✅ Email sent successfully! ID: {email['id']}")
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")