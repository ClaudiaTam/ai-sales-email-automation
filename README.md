# Simple AI Data Analyst & Email Report Automation

This project turns a messy e‑commerce sales CSV into a cleaned dataset, key business metrics, and a short AI-written action plan, then emails the results to non‑technical stakeholders automatically.

Built with:
- n8n (workflow orchestration, AI call, email delivery)
- Hugging Face Spaces (Python cleaning API host)
- Python (data cleaning & metric calculation)
- Gmail (email sending)
- Google Gemini Chat Model (AI text summary)

---

## Demo

- **45‑second walkthrough:** shows the full flow from CSV upload to email dashboard.
- Recommended placement:
  - If hosted: add the link here (YouTube / Hugging Face / GitHub).
  - If stored in this repo: `demo/demo.mp4`.

The demo makes it easy for recruiters to understand the end‑to‑end behavior without reading code.

---

## What the workflow does

1. **Upload a messy CSV**
   - A business user uploads an e‑commerce sales CSV via an n8n Form Trigger.

2. **Clean and calculate in Hugging Face**
   - n8n sends the file to a Python API hosted on Hugging Face Spaces.
   - The script:
     - trims white spaces
     - handles missing values
     - isolates corrupted rows
     - tracks revenue lost in `Cancelled` / `Returned` orders
     - computes totals and core KPIs.

3. **Generate AI consultant insights**
   - An AI step takes the metrics and writes a short, 3‑sentence action plan:
     - leak health check
     - inventory/marketing directive for the top product line
     - 24‑hour execution mandate for the sales team.

4. **Send an email dashboard**
   - A Code node formats the numbers and AI text into a simple HTML scorecard.
   - The Gmail node sends the dashboard email to the stakeholder.

---

## n8n workflow structure

This is the end‑to‑end node sequence you designed (also visible in `n8n_workflow.json`):

1. **On form submission (Form Trigger)**  
   - Input: CSV file uploaded by the user.  
   - Role: starts the workflow whenever a new file is submitted.

2. **HTTP Request (Hugging Face API)**  
   - Method: `POST` to `https://claudiadec2-eda-cleaner-api.hf.space/analyze`.  
   - Role: sends the CSV to the Python backend and returns cleaned metrics as JSON.

3. **AI Agent (Google Gemini Chat Model)**  
   - Role: converts raw metrics into a structured 3‑sentence business recommendation.  
   - Guardrails: no technical database terms, consultant tone only.

4. **Code in JavaScript (HTML formatter)**  
   - Role: builds a minimal HTML email with KPI cards, an AI insight box, and a top‑products table.

5. **Send a message (Gmail)**  
   - Role: emails the HTML report to the stakeholder’s inbox.

The visual n8n canvas (Form → HTTP Request → AI Agent → Code → Gmail) demonstrates clear orchestration, external API integration, AI usage, and presentation logic in one flow.

---

## Key business features

- **Financial snapshot**
  - Gross revenue, average order value (AOV), and total transaction count.

- **Leakage tracker**
  - Money lost or at risk due to `Cancelled` / `Returned` orders.

- **Top product lines**
  - Ranks the 3 highest‑revenue product codes from the uploaded CSV.

- **Non‑technical copy**
  - AI text is forced to sound like a corporate consultant and avoid database jargon.

---

## Files in this repo

- `README.md` – project overview for recruiters and reviewers.
- `app.py` – Hugging Face Space backend for CSV cleaning and metric generation.
- `requirements.txt` – Python dependencies for the Space.
- `Dockerfile` – container setup used by Hugging Face.
- `n8n_workflow.json` – exportable n8n workflow (Form → HF API → AI → Email).
- `demo/demo.mp4` (optional) – short video demo of the full pipeline.

---

## How to run a quick demo

1. Import `n8n_workflow.json` into your n8n instance.
2. Configure credentials:
   - Hugging Face API URL
   - Gmail
   - Google Gemini API / LLM key
3. Open the Form Trigger URL and upload a sample messy CSV.
4. Wait for the workflow to complete and check your inbox for the HTML dashboard email.

This project is designed as a portfolio piece to show end‑to‑end automation for sales reporting: from raw CSV to AI‑assisted email summary, using n8n and Hugging Face Spaces together.
