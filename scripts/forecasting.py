from prophet import Prophet
import pandas as pd
import logging

# Suppress Prophet logs
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

class Forecaster:
    """
    Forecasting Engine using Facebook Prophet.
    """
    def __init__(self, clean_df: pd.DataFrame):
        self.df = clean_df

    def predict_revenue(self, periods=90) -> pd.DataFrame:
        """
        Predicts Gross Revenue (Invoices Issued) for the next `periods` days.
        """
        # Prepare data for Prophet (ds, y)
        daily_revenue = self.df.groupby('issue_date')['total_amount'].sum().reset_index()
        daily_revenue.columns = ['ds', 'y']
        
        # Remove timezone if present for Prophet compatibility
        daily_revenue['ds'] = daily_revenue['ds'].dt.tz_localize(None)
        
        # Model
        m = Prophet(daily_seasonality=False, yearly_seasonality=True)
        m.fit(daily_revenue)
        
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def predict_cash_flow(self, periods=90) -> pd.DataFrame:
        """
        Predicts Realized Cash (Payments) for the next `periods` days.
        """
        # Prepare data: Payments made on `paid_on_date`
        payments = self.df[self.df['paid_on_date'].notna()].copy()
        daily_cash = payments.groupby('paid_on_date')['total_amount'].sum().reset_index()
        daily_cash.columns = ['ds', 'y']
        
        daily_cash['ds'] = daily_cash['ds'].dt.tz_localize(None)
        
        if len(daily_cash) < 20: 
            # Not enough data points
            return pd.DataFrame()

        m = Prophet(daily_seasonality=False, yearly_seasonality=True)
        m.fit(daily_cash)
        
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
