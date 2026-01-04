import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

class Analyzer:
    """
    Core Analytical Engine for Customer Segmentation and Risk Assessment.
    """
    def __init__(self, clean_df: pd.DataFrame):
        self.df = clean_df
        self.payment_data = self._prepare_payment_data()

    def _prepare_payment_data(self):
        """
        Prepares aggregated data at payer level.
        """
        # Filter for relevant transactions
        # We look at historical behavior
        return self.df.groupby('payer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'days_late': 'mean',
            'status': lambda x: (x == 'Overdue').sum()
        }).reset_index()

    def calculate_rfm_segments(self) -> pd.DataFrame:
        """
        Performs RFM (Recency, Frequency, Monetary) Segmentation.
        Returns a DataFrame with 'Segment' labels.
        """
        rfm = self.df.groupby('payer_id').agg({
            'issue_date': lambda x: (self.df['issue_date'].max() - x.max()).days, # Recency
            'id': 'count', # Frequency
            'total_amount': 'sum' # Monetary
        }).reset_index()
        
        rfm.columns = ['payer_id', 'Recency', 'Frequency', 'Monetary']
        
        # Scoring (Simple Quintiles)
        # Recency: Lower is better (5 is best)
        # Frequency: Higher is better (5 is best)
        # Monetary: Higher is better (5 is best)
        
        labels = [5, 4, 3, 2, 1] # for Recency
        rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), q=5, labels=labels)
        
        labels = [1, 2, 3, 4, 5] # for F and M
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=labels)
        rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=labels)
        
        # Convert to int
        rfm['R_Score'] = rfm['R_Score'].astype(int)
        rfm['F_Score'] = rfm['F_Score'].astype(int)
        rfm['M_Score'] = rfm['M_Score'].astype(int)
        
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        rfm['RFM_Sum'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        
        # Define Segments based on Score (Business-Focused Strategy)
        def segment_rfm(x):
            if x >= 13: return 'Top Value Accounts'      # Formerly Champions
            elif x >= 10: return 'Core Revenue Accounts' # Formerly Loyal
            elif x >= 7: return 'Growth Opportunities'   # Formerly Potentially Loyal
            elif x >= 5: return 'High-Risk Accounts'     # Formerly At Risk
            else: return 'Inactive Accounts'             # Formerly Lost
            
        rfm['Segment'] = rfm['RFM_Sum'].apply(segment_rfm)
        return rfm

    def calculate_dso(self, period='ME') -> pd.DataFrame:
        """
        Calculates Days Sales Outstanding trend using a simplified method:
        (Total AR / Total Credit Sales) * Number of Days in Period.
        Aggregated by Month.
        """
        # Resample to monthly (ME = Month End)
        monthly = self.df.set_index('issue_date').resample(period).agg({
            'total_amount': 'sum', # Total Credit Sales
            'amount_due': 'sum' # Approximation of ending AR for that vintage
        }).reset_index()
        
        # Simple DSO formulation for trend analysis
        # Note: True DSO requires rolling windows of AR balance, 
        # but for this dataset "amount_due" roughly proxies the *remaining* AR from that month's sales.
        # A better proxy for "Ending AR" given transaction data is:
        # Cumulative Sum of (Issued - Paid) over time.
        
        # Let's build a proper daily AR balance
        daily_transactions = []
        for _, row in self.df.iterrows():
            daily_transactions.append({'date': row['issue_date'], 'change': row['total_amount']})
            if pd.notna(row['paid_on_date']):
                daily_transactions.append({'date': row['paid_on_date'], 'change': -row['total_amount']}) # Assuming full payment
                
        ar_flow = pd.DataFrame(daily_transactions).sort_values('date')
        if not ar_flow.empty:
            ar_flow['ar_balance'] = ar_flow['change'].cumsum()
            # Resample to monthly average
            dso_trend = ar_flow.set_index('date').resample(period)['ar_balance'].mean().reset_index()
            
            # Get Monthly Sales for ratio
            sales = self.df.set_index('issue_date').resample(period)['total_amount'].sum().reset_index()
            
            merged = pd.merge(dso_trend, sales, left_on='date', right_on='issue_date')
            merged['DSO'] = (merged['ar_balance'] / merged['total_amount'].replace(0, 1)) * 30 # Standard 30 day window
            return merged
        return pd.DataFrame()

    def calculate_risk_score(self) -> pd.DataFrame:
        """
        Calculates a Risk Score (0-100) for each open invoice/customer.
        High Score = High Probability of Default.
        """
        # Aggregate Risk Factors
        risk = self.df.groupby('payer_id').agg({
            'days_late': 'mean', # Avg lateness
            'amount_due': 'sum'  # Total Exposure
        }).reset_index()
        
        # Normalize
        scaler = StandardScaler()
        # Handle nan
        risk = risk.fillna(0)
        
        if not risk.empty:
            features = risk[['days_late', 'amount_due']]
            normalized = scaler.fit_transform(features)
            
            # Simple weighted sum for score: 70% Lateness, 30% Amount Size
            # We use sigmoid to bound 0-100
            weights = np.array([0.7, 0.3]) 
            raw_score = np.dot(normalized, weights)
            
            # Sigmoid transform to 0-100
            risk['Risk_Score'] = 100 / (1 + np.exp(-raw_score))
        else:
            risk['Risk_Score'] = 0
            
        return risk

    def calculate_write_offs(self, threshold_days=90) -> pd.DataFrame:
        """
        Calculates potential write-offs over time.
        Definition: Invoices that are > 90 days late are considered 'Write-off Risk'.
        """
        # We need to look at historical snapshot. 
        # For simplicity in this demo, we group the CURRENTLY overdue items by their issue month.
        # This shows "Which months generated the bad debt?"
        
        overdue = self.df[
            (self.df['status'] == 'Overdue') & 
            (self.df['days_late'] > threshold_days)
        ].copy()
        
        if overdue.empty:
            return pd.DataFrame(columns=['month', 'write_off_amount'])

        monthly_write_offs = overdue.set_index('issue_date').resample('ME')['amount_due'].sum().reset_index()
        monthly_write_offs.columns = ['month', 'write_off_amount']
        
        return monthly_write_offs

    def get_collection_strategy(self, segment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Maps Customer Segments to Actionable Strategies.
        Part 2B of the Assignment.
        """
        strategies = {
            'Top Value Accounts': 'No Reminder Required (Monitor Only)',
            'Core Revenue Accounts': 'Automated Email (Day 3 Overdue)',
            'Growth Opportunities': 'Automated SMS + Email (Day 1 Overdue)',
            'High-Risk Accounts': 'Personal Call from AR Specialist (Day -3 Pre-due)',
            'Inactive Accounts': 'Re-engagement Campaign / Dunning Process',
            'Unknown': 'Verify Data'
        }
        
        segment_df['Recommended_Action'] = segment_df['Segment'].map(strategies)
        return segment_df
