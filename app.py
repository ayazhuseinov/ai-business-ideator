import streamlit as st
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from xml.sax.saxutils import escape
from io import BytesIO

# Register built-in Chinese font (renders 企查查, ¥, etc.)
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
CN_FONT = "STSong-Light"

load_dotenv()

# Streamlit config
st.set_page_config(page_title="AI Business Ideator", layout="wide")
st.title("🚀 AI Business Ideator")
st.markdown("Generate startup ideas tailored to China market — with financial analysis & validation checklist.")
# Access gate (protects API credits on public deployment)
app_password = os.getenv("APP_PASSWORD")
if app_password:
    entered = st.text_input("Access code", type="password")
    if entered != app_password:
        st.info("Enter the access code to use the app. Contact the author for access.")
        st.stop()
# Initialize Zhipu client
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    st.error("❌ ZHIPU_API_KEY not found in .env file. Please add it.")
    st.stop()

client = ZhipuAI(api_key=api_key)
if "ideas_data" not in st.session_state:
    st.session_state.ideas_data = None

# Function to generate PDF
def generate_pdf(ideas_data, market):
    """Generate PDF from ideas data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1,
        fontName=CN_FONT
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#ff7f0e'),
        spaceAfter=8,
        fontName=CN_FONT
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=CN_FONT,
        fontSize=10,
        leading=14
    )

    def t(value):
        """Safe text: string + escape &, <, > so reportlab doesn't crash"""
        return escape(str(value if value is not None else 'N/A'))
    
    # Title
    story.append(Paragraph("AI Business Ideator — China Market Startup Ideas", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Market Focus: <b>{t(market)}</b>", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Ideas
    for i, idea in enumerate(ideas_data.get("ideas", []), 1):
        # Idea heading
        story.append(Paragraph(f"Idea {i}: {t(idea.get('name', 'Unnamed'))}", heading_style))
        
        # Business Model
        story.append(Paragraph(f"<b>Target Customer:</b> {t(idea.get('target_customer', 'N/A'))}", body_style))
        story.append(Paragraph(f"<b>Revenue Model:</b> {t(idea.get('revenue_model', 'N/A'))}", body_style))
        story.append(Paragraph(f"<b>Market Size:</b> {t(idea.get('market_size', 'N/A'))}", body_style))
        story.append(Paragraph(f"<b>Competition:</b> {t(idea.get('competition_level', 'N/A'))}", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Competitors
        if idea.get("key_competitors"):
            story.append(Paragraph("<b>Key Competitors:</b>", body_style))
            for comp in idea.get("key_competitors", []):
                story.append(Paragraph(f"- {t(comp)}", body_style))
            story.append(Spacer(1, 0.1*inch))
        
        # China Market
        story.append(Paragraph("<b>Chinese Platforms:</b>", body_style))
        for platform in idea.get("chinese_platforms", []):
            story.append(Paragraph(f"- {t(platform)}", body_style))
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph(f"<b>Supply Chain:</b> {t(idea.get('supply_chain_notes', 'N/A'))}", body_style))
        story.append(Paragraph(f"<b>Go-to-Market:</b> {t(idea.get('go_to_market_china', 'N/A'))}", body_style))
        story.append(Paragraph(f"<b>Regulatory:</b> {t(idea.get('regulatory_notes', 'N/A'))}", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Financial Analysis
        fin = idea.get("financial_analysis", {})
        fin_data = [
            ["Metric", "Value"],
            ["Year 1 Revenue", f"${fin.get('year1_revenue', 0):,.0f}"],
            ["Year 3 Revenue", f"${fin.get('year3_revenue', 0):,.0f}"],
            ["Initial Investment", f"${fin.get('initial_investment', 0):,.0f}"],
            ["Gross Margin", f"{fin.get('gross_margin_pct', 0):.0f}%"],
            ["IRR", f"{fin.get('irr_pct', 0):.1f}%"],
            ["5-Year NPV (5%)", f"${fin.get('npv_5yr_pct', 0):,.0f}"],
        ]
        
        fin_table = Table(fin_data, colWidths=[3*inch, 2*inch])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(fin_table)
        story.append(Spacer(1, 0.15*inch))
        
        # 90-Day Launch Plan
        story.append(Paragraph("<b>90-Day China Launch Plan:</b>", body_style))
        for j, step in enumerate(idea.get("launch_plan", []), 1):
            story.append(Paragraph(f"{j}. {t(step)}", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Risks
        story.append(Paragraph("<b>Top 3 Risks & Mitigation:</b>", body_style))
        for risk in idea.get("top_3_risks", []):
            story.append(Paragraph(f"- {t(risk)}", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Validation
        story.append(Paragraph("<b>How to Validate:</b>", body_style))
        story.append(Paragraph("<b>Websites to Research:</b>", body_style))
        val = idea.get("validation_checklist", {})
        for website in val.get("websites_to_research", []):
            story.append(Paragraph(f"- {t(website)}", body_style))
        story.append(Paragraph(f"<b>Steps:</b> {t(val.get('how_to_validate', 'N/A'))}", body_style))
        
        # Page break between ideas (except last one)
        if i < len(ideas_data.get("ideas", [])):
            story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Sidebar inputs
with st.sidebar:
    st.header("Your Profile")
    
    skills = st.text_area(
        "Your Skills (comma-separated)",
        placeholder="e.g., Python, Supply Chain, B2B Sales, AI/ML",
        height=100
    )
    
    capital = st.slider("Available Capital ($)", 0, 100000, 50000)
    capital_rmb = capital * 7  # Rough conversion
    
    market = st.selectbox(
        "Market Interest",
        ["Supply Chain", "E-commerce", "Electric Devices", "Generators", "Hardware"]
    )
    
    timeline = st.slider("Timeline (months)", 1, 24, 6)
    
    risk_tolerance = st.selectbox(
        "Risk Tolerance",
        ["Low", "Medium", "High"]
    )
    
    education = st.selectbox(
        "Education Level",
        ["High School", "Bachelor", "Master", "PhD"]
    )
    
    industry_exp = st.slider("Years of Industry Experience", 0, 20, 2)
    
    geographic = st.selectbox(
        "Geographic Focus",
        ["Asia", "Europe", "North America", "Global", "Middle East"]
    )
    
    team_size = st.slider("Expected Team Size at Launch", 1, 20, 3)
    
    st.divider()
    st.caption("✅ All fields ready. Click button to generate.")

# Main form
if st.button("🎯 Generate 5 China-Focused Business Ideas", use_container_width=True, type="primary"):
    if not skills or not market:
        st.error("❌ Please fill in Skills and Market Interest")
    else:
        with st.spinner("🤖 Generating ideas with Zhipu GLM-5.3..."):
            # Build system prompt (OPTIMIZED - SHORT)
            system_prompt = """You are an expert China market startup strategist.
Generate 5 innovative startup ideas specifically for Mainland China.

RETURN ONLY VALID JSON. No markdown, no explanations.

Structure:
{
  "ideas": [
    {
      "name": "Business Name",
      "target_customer": "Who buys this in China",
      "revenue_model": "How you make money",
      "market_size": "TAM estimate (¥XBN in China)",
      "competition_level": "High/Medium/Low",
      "key_competitors": ["Alibaba", "JD.com", "etc."],
      "chinese_platforms": ["Taobao", "1688", "WeChat", "Douyin", "Pinduoduo"],
      "supply_chain_notes": "Source: Yiwu/Shenzhen/1688. Logistics strategy.",
      "go_to_market_china": "Use WeChat Pay/Alipay. Which platforms.",
      "regulatory_notes": "ICP filing, data localization, compliance.",
      "launch_plan": ["Day 1-17: Step 1", "Day 18-34: Step 2", "Day 35-51: Step 3", "Day 52-68: Step 4", "Day 69-90: Step 5"],
      "top_3_risks": ["Risk 1 + mitigation", "Risk 2 + mitigation", "Risk 3 + mitigation"],
      "validation_checklist": {
        "websites_to_research": ["企查查", "1688", "Pinduoduo", "Taobao"],
        "how_to_validate": "Check competitors on 企查查, search demand on Pinduoduo, verify supplier costs on 1688, calculate 60-70% margins"
      },
      "financial_analysis": {
        "year1_revenue": 150000,
        "year3_revenue": 1500000,
        "initial_investment": 50000,
        "gross_margin_pct": 60,
        "irr_pct": 85,
        "npv_5yr_pct": 450000,
        "currency_note": "USD"
      }
    }
  ]
}
"""

            user_message = f"""Generate 5 China-market startup ideas for:
- Skills: {skills}
- Capital: ${capital:,} (¥{capital_rmb:,.0f})
- Market: {market}
- Timeline: {timeline} months
- Risk: {risk_tolerance}
- Experience: {industry_exp} years
- Team: {team_size} people

Requirements:
1. Ideas match "{market}" in Mainland China
2. Named competitors (Alibaba, JD, Pinduoduo, 1688, etc.)
3. Realistic supply chain (Yiwu, Shenzhen, 1688)
4. China platforms (WeChat, Taobao, 1688, Douyin, Pinduoduo)
5. ICP filing + data localization notes
6. 60-70% gross margins (China e-commerce realistic)
7. Achievable in {timeline} months with ${capital:,}
8. 90-day launch plan
9. China-specific risks (regulatory, platform algorithm, RMB fluctuation)
10. Validation websites (企查查, 1688, Pinduoduo, Taobao)
"""

            try:
                response = client.chat.completions.create(
                    model="glm-5.3",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Clean JSON if wrapped in markdown
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                ideas_data = json.loads(response_text)
                st.session_state.ideas_data = ideas_data
                
                # Display ideas
                st.success("✅ Ideas generated successfully!")
                st.divider()
                
                for i, idea in enumerate(ideas_data.get("ideas", []), 1):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.subheader(f"{i}. {idea.get('name', 'Unnamed Idea')}")
                        
                        with col2:
                            fin = idea.get("financial_analysis", {})
                            st.metric("IRR", f"{fin.get('irr_pct', 0):.1f}%")
                        
                        # Business Model
                        with st.expander("📊 Business Model", expanded=(i==1)):
                            st.write(f"**Target Customer:** {idea.get('target_customer')}")
                            st.write(f"**Revenue Model:** {idea.get('revenue_model')}")
                            st.write(f"**Market Size (TAM):** {idea.get('market_size')}")
                            st.write(f"**Competition Level:** {idea.get('competition_level')}")
                            
                            if idea.get("key_competitors"):
                                st.write("**Key Competitors:**")
                                for comp in idea.get("key_competitors", []):
                                    st.write(f"  • {comp}")
                        
                        # China Market Insights
                        with st.expander("🇨🇳 China Market Insights"):
                            if idea.get("chinese_platforms"):
                                st.write("**Chinese Platforms to Use:**")
                                for platform in idea.get("chinese_platforms", []):
                                    st.write(f"  • {platform}")
                            
                            st.write(f"**Supply Chain:** {idea.get('supply_chain_notes')}")
                            st.write(f"**Go-to-Market Strategy:** {idea.get('go_to_market_china')}")
                            st.write(f"**Regulatory Notes:** {idea.get('regulatory_notes')}")
                        
                        # Financial Projections
                        with st.expander("💰 Financial Projections"):
                            fin = idea.get("financial_analysis", {})
                            fcol1, fcol2, fcol3 = st.columns(3)
                            with fcol1:
                                st.metric("Year 1 Revenue", f"${fin.get('year1_revenue', 0):,.0f}")
                            with fcol2:
                                st.metric("Year 3 Revenue", f"${fin.get('year3_revenue', 0):,.0f}")
                            with fcol3:
                                st.metric("Initial Investment", f"${fin.get('initial_investment', 0):,.0f}")
                            
                            fcol4, fcol5, fcol6 = st.columns(3)
                            with fcol4:
                                st.metric("Gross Margin", f"{fin.get('gross_margin_pct', 0):.0f}%")
                            with fcol5:
                                st.metric("IRR", f"{fin.get('irr_pct', 0):.1f}%")
                            with fcol6:
                                st.metric("5-Year NPV (5%)", f"${fin.get('npv_5yr_pct', 0):,.0f}")
                            
                            if fin.get("currency_note"):
                                st.caption(f"💱 {fin.get('currency_note')}")
                        
                        # 90-Day Launch Plan
                        with st.expander("🚀 90-Day China Launch Plan"):
                            for j, step in enumerate(idea.get("launch_plan", []), 1):
                                st.write(f"**Phase {j}:** {step}")
                        
                        # Risks & Mitigation
                        with st.expander("⚠️ Top 3 Risks & Mitigation"):
                            for risk in idea.get("top_3_risks", []):
                                st.write(f"• {risk}")
                        
                        # Validation Checklist
                        with st.expander("📋 How to Validate This Idea"):
                            val = idea.get("validation_checklist", {})
                            st.write("**Websites to Research:**")
                            for website in val.get("websites_to_research", []):
                                st.write(f"  • {website}")
                            
                            st.write("\n**Step-by-Step Validation:**")
                            st.write(val.get("how_to_validate", "Follow the steps to verify market demand, competition, and margins."))
                        
                        st.divider()
                
                # Export section
                st.success("✅ **All 5 ideas generated! Ready for investor presentation.**")
                st.info("📋 **NEXT STEP:** Download PDF and use the validation checklist to verify each idea with real Chinese market data before presenting to investor.")
                
                # PDF Download button
                pdf_data = generate_pdf(ideas_data, market)
                st.download_button(
                    label="📄 Download All Ideas as PDF",
                    data=pdf_data,
                    file_name=f"business_ideas_{market.replace(' ', '_')}_China.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    on_click="ignore"
                )
                
                # JSON Download button (optional backup)
                st.download_button(
                    label="📋 Download All Ideas as JSON (Backup)",
                    data=json.dumps(ideas_data, indent=2, ensure_ascii=False),
                    file_name=f"business_ideas_{market.replace(' ', '_')}_China.json",
                    mime="application/json",
                    use_container_width=True,
                    on_click="ignore"
                )
            
            except json.JSONDecodeError as e:
                st.error(f"❌ Failed to parse AI response: {str(e)}")
                st.info("Try again — sometimes the API returns malformed JSON on first attempt.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Check your ZHIPU_API_KEY in .env file or try again later.")