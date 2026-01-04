# Machine Learning Experiment Report

**Date:** May 22, 2024
**Model Type:** Random Forest Regressor & Classifier
**Training Size:** 12,029 Closed Invoices

## 1. Executive Summary of ML Performance
We conducted a rapid experiment to determine if Machine Learning could outperform standard business rules for predicting payment dates.

*   **Result**: The ML model outperformed the baseline average by **31%**.
*   **Recommendation**: While statistically superior, we recommend **retaining the Heuristic Model** for the Phase 1 deployment due to interpretability and data quality concerns (see *Heuristics vs ML Comparison* doc).

## 2. Model Performance Metrics

### Regression: Predicting "Days to Pay"
We attempted to predict exactly how many days after issuance a customer would pay.
*   **Baseline (Mean)**: 42.80 Days Mean Absolute Error (MAE)
*   **Random Forest**: 29.60 Days Mean Absolute Error (MAE)
*   **Improvement**: +13.2 Days accuracy per invoice.

### Classification: Predicting Bad Debt (>90 Days Overdue)
We attempted to flag invoices that would dangerously exceed terms.
*   **Precision (High Risk)**: 53% (When we say it's risky, we are right ~half the time).
*   **Recall (High Risk)**: 47% (We catch nearly half of all actual bad debts).
*   **Accuracy**: 87% overall.

## 3. Key Drivers (Feature Importance)
The model identified the following as the strongest predictors of payment delay:
1.  **Invoice Amount (57%)**: Larger invoices are consistently paid slower.
2.  **Days to Due (25%)**: Payment terms heavily influence actual payment date.
3.  **Seasonality (18%)**: Month of issue plays a significant role in delay.

## 4. Technical Specifications
*   **Library**: Scikit-Learn (v1.2)
*   **Features**: `log(total_amount)`, `days_to_due`, `month_issue`.
*   **Algorithm**: Random Forest (n_estimators=100).
