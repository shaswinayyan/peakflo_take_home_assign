import pandas as pd
import numpy as np

def audit_data(filepath):
    print("--- Starting Data Audit ---")
    df = pd.read_csv(filepath)
    
    # 1. Total Counts & Checksums
    total_rows = len(df)
    total_amount_sum = df['total_amount'].sum()
    amount_due_sum = df['amount_due'].sum()
    
    print(f"Total Rows: {total_rows}")
    print(f"Checksum (Total Amount): {total_amount_sum:,.2f}")
    print(f"Checksum (Amount Due): {amount_due_sum:,.2f}")
    
    # 2. Key Uniqueness
    unique_ids = df['id'].nunique()
    print(f"Unique IDs: {unique_ids} (Matches Rows: {unique_ids == total_rows})")
    
    # 3. Date Logic
    date_cols = ['issue_date', 'due_date', 'paid_on_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)
        
    # Check: Paid before Issued?
    paid_before_issue = df[df['paid_on_date'] < df['issue_date']]
    print(f"Errors: Paid before Issue: {len(paid_before_issue)}")
    if len(paid_before_issue) > 0:
        print(paid_before_issue[['id', 'issue_date', 'paid_on_date']].head())
        
    # Check: Due before Issued? (Possible but rare - backdating)
    due_before_issue = df[df['due_date'] < df['issue_date']]
    print(f"Warnings: Due before Issue: {len(due_before_issue)}")

    # 4. Numerical Logic
    # Negative Amounts?
    negative_totals = df[df['total_amount'] < 0]
    print(f"Negative Total Amounts: {len(negative_totals)}")
    
    negative_due = df[df['amount_due'] < 0]
    print(f"Negative Amount Due: {len(negative_due)}")
    
    # Due > Total? (Maybe interest/penalties, but usually an error in simple AR)
    due_gt_total = df[df['amount_due'] > df['total_amount']]
    print(f"Errors: Amount Due > Total Amount: {len(due_gt_total)}")
    
    # 5. Missing Values
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    # 6. Outliers / Impossible Values
    # Max Invoice Amount
    print(f"\nMax Invoice Amount: {df['total_amount'].max():,.2f}")
    
    # Max Days to Pay
    df['days_to_pay'] = (df['paid_on_date'] - df['issue_date']).dt.days
    print(f"Max Days to Pay: {df['days_to_pay'].max()}")
    print(f"Min Days to Pay: {df['days_to_pay'].min()}")
    
    # 7. Segment Verification (Recalc)
    # Re-verify the count of 'Paid' status logic from previous script
    # Previous Logic: Paid if paid_on_date is not null
    # Check against Amount Due. If Paid, Amount Due should be 0?
    
    paid_with_due = df[(df['paid_on_date'].notnull()) & (df['amount_due'] > 0)]
    print(f"\nLogic Mismatch: Paid Date exists but Amount Due > 0: {len(paid_with_due)}")
    if len(paid_with_due) > 0:
        print("Potential partial payments or data inconsistency.")
        print(paid_with_due[['id', 'total_amount', 'amount_due', 'paid_on_date']].head())

    not_paid_no_due = df[(df['paid_on_date'].isnull()) & (df['amount_due'] == 0)]
    print(f"Logic Mismatch: No Paid Date but Amount Due == 0: {len(not_paid_no_due)}")
    
    print("\n--- End Audit ---")
    
    # Save audit summary to text for review
    with open('Final/audit_results.txt', 'w') as f:
        f.write(f"Total Rows: {total_rows}\n")
        f.write(f"Checksum Total Amount: {total_amount_sum}\n")
        f.write(f"Paid before Issue Errors: {len(paid_before_issue)}\n")
        f.write(f"Paid with Balance Mismatch: {len(paid_with_due)}\n")
        f.write(f"Settled without Date Mismatch: {len(not_paid_no_due)}\n")

if __name__ == "__main__":
    audit_data('data/data.csv')
