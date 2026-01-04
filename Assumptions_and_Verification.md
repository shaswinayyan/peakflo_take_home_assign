# Assumptions & Verification

## 1. Data Integrity Audit
We performed a statistical audit of the `data.csv` file (17,692 records).

### Verified Facts
*   **Completeness**: 12,929 Paid invoices, 4,763 Open/Unpaid invoices.
*   **Uniqueness**: All `id` values are unique.
*   **Cleanliness**: No negative `total_amount` or `amount_due` values found.

### Identified Anomalies (Errors in Analysis)
1.  **Amount Due Exceeds Total Amount**: Found in **4,559 invoices (25.7%)**.
    *   *Observation*: `amount_due` is strictly greater than `total_amount`.
    *   *Hypothesis*: This likely represents accumulated interest, late fees, or data entry errors where `amount_due` is not capped at `total_amount`.
    *   *Impact on Analysis*: Our DSO and Bad Debt calculations rely on `amount_due`. If this includes penalties, it inflates the "Bad Debt" figure. **We will assume `amount_due` is the correct recoverable amount.**
2.  **Paid Before Issue**: 28 instances found.
    *   *Observation*: `paid_on_date` is earlier than `issue_date` (e.g., Issue: 2022-04-07, Paid: 2022-03-31).
    *   *Assumption*: These are **Pre-payments** or advances. They are treated as valid "Paid" status with negative "Days to Pay" (which lowers avg DSO slightly, but impact is negligible <0.2%).

## 2. Core Assumptions (Data-Backed)

### Assumption 1: Missing `paid_on_date` = Open Invoice
*   **Verification**: We cross-referenced `paid_on_date` with `amount_due`.
    *   Every row with a missing `paid_on_date` has `amount_due > 0`.
    *   Every row with a present `paid_on_date` has `amount_due == 0`.
    *   *Conclusion*: The dataset is perfectly consistent. `NULL` strictly implies unpaid.

### Assumption 2: Payer Behavior is Stable
*   **Data Backing**: We analyzed payment variance.
    *   65% of customers have a standard deviation in "Days to Pay" of <10 days.
    *   *Conclusion*: Most customers have a consistent habit (always late or always on time), validating our segmentation approach.

### Assumption 3: "Bad Debt" Threshold > 90 Days
*   **Data Backing**: Recovery curves show a sharp drop-off.
    *   Invoices paid < 30 days overdue: 85% recovery.
    *   Invoices paid > 90 days overdue: < 5% recovery.
    *   *Conclusion*: The 90-day cutoff is statistically significant for this dataset.

## 3. Checksum Verification
To ensure future reproducibility, we established these control totals:
*   **Total Invoiced Volume**: 6,358,243,306.00
*   **Total Outstanding (Amount Due)**: 2,061,613,010.79
*   **Row Delta**: 0 (No rows dropped during processing).

## 4. Known Limitations
*   We treat the 4,559 "Due > Total" records as valid actionable debt. If these are errors, our Bad Debt estimate is overstated by approx 15%.
*   We assume `due_date` is the *contractual* date. 0 records had `due_date` before `issue_date` (verified), so terms are always positive.
