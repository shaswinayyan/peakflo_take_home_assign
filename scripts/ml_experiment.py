import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, classification_report
from datetime import datetime

# Load Data
df = pd.read_csv('data/data.csv')
for col in ['issue_date', 'due_date', 'paid_on_date']:
    df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)

# Feature Engineering
df['invoice_age_days'] = (datetime.now() - df['issue_date']).dt.days
df['days_to_due'] = (df['due_date'] - df['issue_date']).dt.days
df['month_issue'] = df['issue_date'].dt.month
df['total_amount_log'] = np.log1p(df['total_amount'])

# Recalculate status since we are loading raw data
analysis_date = datetime.now()
conditions = [
    (pd.notnull(df['paid_on_date'])), 
    (pd.isnull(df['paid_on_date']) & (df['due_date'] < analysis_date)),
    (pd.isnull(df['paid_on_date']) & (df['due_date'] >= analysis_date))
]
choices = ['Paid', 'Overdue', 'Open']
df['status'] = np.select(conditions, choices, default='Unknown')

# Target: Days to Pay (for closed invoices)
closed_invoices = df[df['status'] == 'Paid'].copy()
# Recalc status if needed as column might not represent 'Paid' string in raw csv, 
# relying on paid_on_date validity
closed_invoices = df[df['paid_on_date'].notnull()].copy()
closed_invoices['days_actual_to_pay'] = (closed_invoices['paid_on_date'] - closed_invoices['issue_date']).dt.days

# Features
features = ['total_amount_log', 'days_to_due', 'month_issue']
X = closed_invoices[features].fillna(0)
y = closed_invoices['days_actual_to_pay']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model 1: Regression (Predict Date)
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"ML Model MAE (Days to Pay): {mae:.2f} days")
print(f"Baseline (Mean) MAE: {mean_absolute_error(y_test, [y_train.mean()]*len(y_test)):.2f} days")

# Feature Importance
importances = rf.feature_importances_
print("Feature Importances:", dict(zip(features, importances)))

# Model 2: Bad Debt Classifier (Paid > 90 days late vs Paid on time)
# 'Bad' = Days overdue > 90
closed_invoices['is_bad_debt'] = ((closed_invoices['paid_on_date'] - closed_invoices['due_date']).dt.days > 90).astype(int)
y_class = closed_invoices['is_bad_debt']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_class, test_size=0.2, random_state=42)
clf = RandomForestClassifier(class_weight='balanced', random_state=42)
clf.fit(X_train_c, y_train_c)
print("\nClassification Report (Predicting Risk > 90 Days):")
print(classification_report(y_test_c, clf.predict(X_test_c)))
