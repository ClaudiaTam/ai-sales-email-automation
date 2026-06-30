import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
import io

app = FastAPI(title="Business Exception EDA Engine")

@app.post("/analyze")
async def analyze_csv(request: Request):
    form = await request.form()
    uploaded_files = form.getlist("files") or form.getlist("file") or form.getlist("csv")
    
    if not uploaded_files:
        return {"status": "error", "message": "No files uploaded."}

    combined_dfs = []
    
    # 1. Ingest and combine multiple files safely
    for file in uploaded_files:
        contents = await file.read()
        try:
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(contents), encoding='latin1')
            
        df.columns = df.columns.str.strip().str.lower()
        combined_dfs.append(df)
        
    main_df = pd.concat(combined_dfs, ignore_index=True, sort=False) if len(combined_dfs) > 1 else combined_dfs[0]
    total_records = len(main_df)

    # 2. Dynamic Schema Finder (Find revenue/price, category, and status columns without hardcoding)
    rev_col = next((c for c in main_df.columns if any(w in c for w in ['total', 'revenue', 'amount'])), None)
    price_col = next((c for c in main_df.columns if 'price' in c), None)
    qty_col = next((c for c in main_df.columns if any(w in c for w in ['qty', 'quantity'])), None)
    cat_col = next((c for c in main_df.columns if any(w in c for w in ['cat', 'category', 'type', 'product'])), None)
    status_col = next((c for c in main_df.columns if 'status' in c), None)

    # 3. Clean Corrupted Data & Count Broken Rows (Operational Tracker)
    # Track rows that have unreadable or blank text in essential fields
    corrupted_rows = 0
    if price_col:
        initial_nulls = main_df[price_col].isnull().sum()
        main_df[price_col] = pd.to_numeric(main_df[price_col].astype(str).str.replace(r'[^\d\.]', '', regex=True), errors='coerce')
        corrupted_rows += int(main_df[price_col].isnull().sum() - initial_nulls + initial_nulls)
        main_df[price_col] = main_df[price_col].fillna(0)

    if qty_col:
        main_df[qty_col] = pd.to_numeric(main_df[qty_col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(1)

    # Calculate mathematically true Total Revenue column if missing
    if rev_col:
        main_df[rev_col] = pd.to_numeric(main_df[rev_col].astype(str).str.replace(r'[^\d\.]', '', regex=True), errors='coerce').fillna(0)
    elif price_col and qty_col:
        main_df['calculated_total'] = main_df[qty_col] * main_df[price_col]
        rev_col = 'calculated_total'

    # 4. Extract Business Value Insights
    total_revenue = float(main_df[rev_col].sum()) if rev_col else 0.0
    avg_order_value = float(main_df[rev_col].mean()) if rev_col else 0.0

    # Calculate Leakage (Revenue locked in Cancelled or Returned orders)
    revenue_at_risk = 0.0
    if status_col and rev_col:
        main_df[status_col] = main_df[status_col].astype(str).str.strip().str.lower()
        risk_mask = main_df[status_col].isin(['cancelled', 'returned', 'refunded'])
        revenue_at_risk = float(main_df[risk_mask][rev_col].sum())

    # Build Top Category Leaderboard
    category_leaderboard = {}
    if cat_col and rev_col:
        main_df[cat_col] = main_df[cat_col].fillna('Unknown').astype(str).str.strip()
        cat_revenue = main_df.groupby(cat_col)[rev_col].sum().sort_values(ascending=False).head(3).to_dict()
        category_leaderboard = {str(k): round(float(v), 2) for k, v in cat_revenue.items()}

    # 5. Output the Executive Contract
    return {
        "status": "success",
        "snapshot": {
            "files_processed": len(uploaded_files),
            "total_transactions": total_records,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(avg_order_value, 2)
        },
        "operational_leakage": {
            "corrupted_records_count": corrupted_rows,
            "revenue_at_risk_cancelled_returned": round(revenue_at_risk, 2),
            "leakage_percentage_of_total": round((revenue_at_risk / total_revenue * 100), 2) if total_revenue > 0 else 0
        },
        "category_leaderboard_by_revenue": category_leaderboard
    }
