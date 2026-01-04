import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set plots style
sns.set_style("whitegrid")

def load_and_clean_data(filepath):
    """Loads data and converts date columns."""
    df = pd.read_csv(filepath)
    
    date_cols = ['issue_date', 'due_date', 'paid_on_date']
    for col in date_cols:
        # Handling mixed formats if any, but considering standard UTC format based on head()
        df[col] = pd.to_datetime(df[col], errors='coerce')
        # Remove timezone info for easier arithmetic if needed, or keep as is. 
        # Making them timezone-naive is often safer for simple day diffs.
        df[col] = df[col].dt.tz_localize(None)

    return df

def feature_engineering(df):
    """Calculates days_to_pay, overdue status, etc."""
    # Days to Pay (only for paid invoices)
    df['days_to_pay'] = (df['paid_on_date'] - df['issue_date']).dt.days
    
    # Days relative to Due Date (Negative = Early, Positive = Late)
    # If paid: paid_on - due_date
    # If not paid: today (simulation) - due_date ... or just leave as NaN/separate logic
    # For historical analysis of *payment behavior*, we strictly look at closed invoices or currently overdue ones.
    
    df['days_overdue_actual'] = (df['paid_on_date'] - df['due_date']).dt.days
    
    # For open invoices, we can calculate 'current_days_overdue' assuming 'today' is max(issue_date) + some buffer or current date.
    # Let's assume 'today' for the analysis is the max date in the dataset + 1 day
    max_date = df['issue_date'].max()
    analysis_date = max_date if pd.notnull(max_date) else datetime.now()
    
    # Status
    conditions = [
        (pd.notnull(df['paid_on_date'])), 
        (pd.isnull(df['paid_on_date']) & (df['due_date'] < analysis_date)),
        (pd.isnull(df['paid_on_date']) & (df['due_date'] >= analysis_date))
    ]
    choices = ['Paid', 'Overdue', 'Open']
    df['status'] = np.select(conditions, choices, default='Unknown')
    
    # Current overdue days for unpaid
    df['current_days_overdue'] = (analysis_date - df['due_date']).dt.days
    df.loc[df['status'] != 'Overdue', 'current_days_overdue'] = np.nan
    
    return df, analysis_date

def segment_customers(df):
    """Segments customers based on payment behavior."""
    # Aggregation per payer
    # We only care about closed (Paid) invoices for *behavior* analysis usually, 
    # but open overdue ones also signal risk.
    
    # Metrics:
    # 1. Avg Day diff from Due Date (Avg Late Days). 
    # 2. % of invoices paid late.
    # 3. Total amount paid vs total amount due.
    
    # Filter for invoices that have a clear outcome (Paid) to judge speed
    paid_invoices = df[df['status'] == 'Paid'].copy()
    
    payer_stats = paid_invoices.groupby('payer_id').agg({
        'days_overdue_actual': 'mean',
        'id': 'count',
        'total_amount': 'sum'
    }).rename(columns={'days_overdue_actual': 'avg_days_late', 'id': 'paid_count', 'total_amount': 'total_paid_vol'})
    
    # Add open/overdue stats
    all_stats = df.groupby('payer_id').agg({
        'id': 'count',
        'total_amount': 'sum',
        'amount_due': 'sum'
    }).rename(columns={'id': 'total_count', 'total_amount': 'total_lifetime_vol', 'amount_due': 'current_outstanding'})
    
    # Merge
    customer_df = all_stats.join(payer_stats)
    customer_df['avg_days_late'] = customer_df['avg_days_late'].fillna(0) # Logic: if never paid, we don't know lag, but maybe check overdue
    
    # Define Segments
    # 1. Prompt: Avg Late <= 0
    # 2. Slow but Steady: 0 < Avg Late <= 15
    # 3. Late/Risk: Avg Late > 15
    # 4. Ghost/Inactive: No payments made ever, but has balance? Or just high outstanding relative to volume.
    
    def classify(row):
        # Specific check for accounts with 0 payments
        if pd.isna(row['paid_count']): 
            return 'High Risk / Non-Payer'
            
        if row['avg_days_late'] <= 0:
            return 'Prompt Payer'
        elif row['avg_days_late'] <= 15:
            return 'Slow but Steady'
        elif row['avg_days_late'] <= 45:
            return 'Late Payer'
        else:
            return 'Very Late / Risk'

    customer_df['segment'] = customer_df.apply(classify, axis=1)
    
    return customer_df

def calculate_dso(df):
    """Calculates monthly DSO."""
    # Simplified DSO = (Total Receivables / Total Credit Sales) * Number of Days
    # We will do a monthly trend.
    # Group by Issue Month.
    df['issue_month'] = df['issue_date'].dt.to_period('M')
    
    monthly = df.groupby('issue_month').agg({
        'total_amount': 'sum',
        'amount_due': 'sum' # This is snapshot based, might not be accurate for historical DSO.
    })
    
    # Correct Historical DSO Approach:
    # "Count back" method or simplified: (Ending AR / Credit Sales) * Days.
    # Since we have transactional data, we can reconstruct AR at each month end.
    # AR at Month End = Sum of (invoices issued before month end AND (paid_after month_end OR never paid))
    
    dates = pd.period_range(start=df['issue_date'].min().to_period('M'), end=df['issue_date'].max().to_period('M'), freq='M')
    
    dso_data = []
    
    for period in dates:
        month_end = period.to_timestamp(how='end')
        month_start = period.to_timestamp(how='start')
        
        # Sales in this month (or lookback 3 months for standard DSO)
        # Standard DSO often uses 90 days lookback sales.
        lookback_start = month_end - timedelta(days=90)
        
        credit_sales_window = df[(df['issue_date'] >= lookback_start) & (df['issue_date'] <= month_end)]['total_amount'].sum()
        
        # Receivables at month end
        # Issued on or before month_end
        # AND (Paid > month_end OR Not Paid)
        ar_at_end = df[
            (df['issue_date'] <= month_end) & 
            ((df['paid_on_date'] > month_end) | (df['paid_on_date'].isnull()))
        ]['total_amount'].sum()
        
        if credit_sales_window > 0:
            dso = (ar_at_end / credit_sales_window) * 90
        else:
            dso = 0 # or nan
            
        dso_data.append({'month': period, 'dso': dso, 'ar': ar_at_end, 'sales_90d': credit_sales_window})
        
    return pd.DataFrame(dso_data)

def predict_bad_debt(df):
    """Identifies potential bad debt."""
    # Criteria: Overdue > 90 days
    # We will tag specific invoices.
    
    # Using 'current_days_overdue' calculated in feature_engineering
    # If status is Overdue and days > 90 -> Likely Bad Debt
    
    bad_debt_mask = (df['status'] == 'Overdue') & (df['current_days_overdue'] > 90)
    bad_debt_amount = df.loc[bad_debt_mask, 'amount_due'].sum()
    
    # Monthly Write-off trend (simulated based on when they crossed 90 days)
    # We can estimate "write-off date" as due_date + 90 days
    df['simulated_writeoff_date'] = df['due_date'] + timedelta(days=90)
    
    writeoff_trend = df[bad_debt_mask].groupby(df['simulated_writeoff_date'].dt.to_period('M'))['amount_due'].sum()
    
    return bad_debt_amount, writeoff_trend

def forecast_revenue(df, analysis_date):
    """Forecasts revenue for next 3 months."""
    # 1. Realized Revenue from Existing AR (Open Invoices)
    # We need a probability of payment curve or simple assumption.
    # Assumption: 
    # - < 30 days overdue: 90% collection chance next month.
    # - 30-60 days overdue: 50% collection chance.
    # - > 60 days: 10% chance.
    # - Not due yet: 95% chance on due date.
    
    # We project WHEN it will be paid.
    # If not due: expect payment on due_date.
    # If overdue: expect payment in next 30 days (simplified).
    
    open_invoices = df[df['status'] == ('Open')].copy()
    overdue_invoices = df[df['status'] == ('Overdue')].copy()
    
    # Future Collections (Month 1, 2, 3)
    forecast = {
        'Month 1': 0,
        'Month 2': 0,
        'Month 3': 0
    }
    
    # Current month start
    current_month_start = analysis_date.replace(day=1)
    
    # Helper for bucketing
    def get_month_bucket(date_val):
        diff = (date_val.year - current_month_start.year) * 12 + (date_val.month - current_month_start.month)
        if diff == 0: return 'Month 1'
        if diff == 1: return 'Month 2'
        if diff == 2: return 'Month 3'
        return 'Later'

    # 1. From Open (Not Overdue)
    for _, row in open_invoices.iterrows():
        # Expected pay date = due date
        bucket = get_month_bucket(row['due_date'])
        if bucket in forecast:
            forecast[bucket] += row['amount_due'] * 0.95 # Risk adjustment
            
    # 2. From Overdue
    # Assume we collect a portion in Month 1, then write off.
    # < 30 days overdue -> 80% in Month 1
    # > 30 days -> 20% in Month 1
    for _, row in overdue_invoices.iterrows():
        bucket = 'Month 1' # Collect ASAP
        if row['current_days_overdue'] < 30:
             forecast[bucket] += row['amount_due'] * 0.8
        elif row['current_days_overdue'] < 60:
             forecast[bucket] += row['amount_due'] * 0.4
        else:
             forecast[bucket] += row['amount_due'] * 0.05
             
    # 3. From New Sales (Gross Revenue)
    # Average monthly sales last 3 months
    recent_sales = df[df['issue_date'] > (analysis_date - timedelta(days=90))]['total_amount'].sum() / 3
    
    # Project new sales for M1, M2, M3
    # If payment terms are 30 days, M1 sales are collected in M2.
    # M1 Sales -> Collect M2
    # M2 Sales -> Collect M3
    # M3 Sales -> Collect M4 (outside scope)
    
    forecast['Month 1'] += 0 # Collections from M1 sales happen in M2 usually
    forecast['Month 2'] += recent_sales * 0.9 # Collect M1 sales
    forecast['Month 3'] += recent_sales * 0.9 # Collect M2 sales
    
    return forecast

def main():
    print("Loading data...")
    df = load_and_clean_data('data/data.csv')
    print(f"Data loaded: {len(df)} rows")
    
    print("Feature engineering...")
    df, analysis_date = feature_engineering(df)
    
    print("Segmenting customers...")
    customer_df = segment_customers(df)
    print("\nSegment Distribution:")
    print(customer_df['segment'].value_counts())
    
    print("\nCalculating DSO...")
    dso_df = calculate_dso(df)
    print("\nLast 5 months DSO:")
    print(dso_df.tail())
    
    print("\nPredicting Bad Debt...")
    bad_debt_val, bad_debt_trend = predict_bad_debt(df)
    print(f"Total Potential Bad Debt (>90 days overdue): {bad_debt_val:,.2f}")
    
    print("\nForecasting Revenue (Net Collections) for next 3 months:")
    forecast = forecast_revenue(df, analysis_date)
    print(forecast)

    # Save processed data for notebook usage or verification
    df.to_csv('Final/processed_invoices.csv', index=False)
    customer_df.to_csv('Final/customer_segments.csv')
    dso_df.to_csv('Final/dso_trend.csv')
    print("\nProcessed files saved to Final/ directory.")

if __name__ == "__main__":
    main()
