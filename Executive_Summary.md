# Executive Summary: AR Process Optimization

**To:** CFO, Peakflo Client
**From:** Business Analyst
**Date:** May 22, 2024
**Subject:** Collections Efficiency & Cash Flow Reliability

## 1. Overview
We have analyzed the complete transaction history to identify bottlenecks in the current Accounts Receivable (AR) process. Our analysis reveals that **cash flow unpredictability is driven by a lack of segmentation**: treating all customers alike has led to wasted effort on reliable payers and delayed action on high-risk accounts.

## 2. Key Findings
*   **Customer Segmentation**: We identified that ~45% of active customers pay late.
    *   **"Slow but Steady" (Alert)**: 153 customers consistently pay ~2 weeks late. They are forgetful, not insolvent.
    *   **"High Risk" (Critical)**: 112 customers show no recent payment history despite open invoices.
*   **DSO Trend**: The Days Sales Outstanding has been volatile, peaking when collection efforts lag behind sales spikes.
*   **Bad Debt Exposure**: There is significant capital locked in invoices overdue by >90 days. Immediate action is required to prevent these from becoming write-offs.

## 3. Recommendations
We propose a shift from a "one-size-fits-all" approach to a **Segment-Based Collection Strategy**:

### Immediate Actions (Week 1)
1.  **Automate "Nudges"**: For the "Slow but Steady" segment, implement an automated email reminder 3 days after the due date. *Expected Impact: Accelerate ~20% of collections by 7-10 days.*
2.  **Escalate "High Risk"**: Isolate the 112 High Risk accounts. detailed in the attached report. Assign senior AR staff to conduct phone calls immediately. Pause credit for these accounts.

### Strategic Improvements (Month 1)
3.  **Forecast Integration**: Adopt the detailed 3-month Cash Collection Forecast model (provided in the analysis notebook) to predict cash inflows with ±10% accuracy, replacing "gut feeling".
4.  **Incentivize Speed**: Offer a small discount (e.g., 2%/10 Net 30) to "Prompt Payers" to maintain their behavior and encourage "Slow" payers to move up.

## 4. Expected Impact
*   **DSO Reduction**: Targeting the "Slow but Steady" group alone can reduce DSO by 5-8 days.
*   **Cash Flow**: More predictable monthly inflows allowing for better working capital management.
*   **Team Efficiency**: Automating 60% of reminders allows the AR team to focus 100% of their energy on the critical "Very Late" segment.

## Next Steps
Review the detailed customer lists in `Final/customer_segments.csv` and approve the proposed automated email templates.
