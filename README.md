# AI Business Ideator — China Market

A Streamlit app that generates five China-market startup ideas from a founder's profile, with go-to-market, regulatory, supply-chain and financial analysis, exportable as a PDF report.

Built with Python, Streamlit and the Zhipu GLM-5.3 API.

**Live demo:** https://ai-businessideator.streamlit.app/ (access code required, contact me via LinkedIn)

## What it does

The user enters a founder profile: skills, available capital, target market, timeline, risk tolerance, education, experience, geographic focus and team size. The app returns five ideas, each with:

- Target customer, revenue model, market size (TAM) and competition level
- Named Chinese competitors and the platforms to sell on (WeChat, Douyin, 1688, Pinduoduo, Taobao)
- Supply-chain notes (Yiwu, Shenzhen, Guangzhou sourcing and logistics)
- Regulatory notes (ICP filing, EDI licence, PIPL data localisation, CAC generative-AI rules)
- A five-phase 90-day launch plan
- Top three China-specific risks with mitigations
- A validation checklist (企查查, 1688, Pinduoduo, Taobao research steps)
- Financial estimates: Year 1 and Year 3 revenue, initial investment, gross margin, IRR, 5-year NPV

Results can be downloaded as a PDF report (Chinese text supported) or as JSON.

## Sample output

See [`samples/`](samples/) for a full PDF report generated for the Supply Chain market.

## Setup

```bash
git clone https://github.com/ayazhuseinov/ai-business-ideator.git
cd ai-business-ideator
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Zhipu API key:

```
ZHIPU_API_KEY=your_key_here
```

Run the app:

```bash
streamlit run app.py
```

Then open http://localhost:8501.

## How it works

1. Sidebar inputs are combined into a structured prompt.
2. GLM-5.3 returns the five ideas as JSON in a fixed schema.
3. The app parses the JSON, renders each idea in expandable sections, and builds the PDF with ReportLab using a built-in CJK font.

Zhipu's servers are in mainland China, so the app runs from China without a VPN.

## Limitations

- **Financial figures are model estimates, not calculations.** IRR and NPV are produced by the LLM rather than computed from cash flows, and should be treated as rough directional numbers.
- **The capital input is not enforced.** Generated ideas can require more initial investment than the capital entered.
- Market sizes and competitor details are not verified against live data. The validation checklist is there for that step.
- Output varies between runs (temperature 0.7).

## Roadmap

- Have the model generate cash-flow assumptions and compute IRR/NPV in Python
- Enforce the capital constraint and flag ideas that exceed it
- Add a one-page summary comparing all five ideas

## Author

Ayaz Huseynov — MSc International Business, Shanghai University
[LinkedIn](https://linkedin.com/in/ayaz-hüseynov) · [Dealbaku](https://github.com/ayazhuseinov/dealbaku)