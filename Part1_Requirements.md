# Part 1: Business Requirements & Problem Definition

## 1. Core Business Problems
The CFO and AR team at the client company are facing three primary challenges:
1.  **Inefficient Collection Process**: The current approach is manual and reactive ("chasing payments manually"), leading to wasted effort on low-priority or reliable customers while potentially neglecting high-risk ones.
2.  **Cash Flow Unpredictability**: The lack of visibility into "reliable vs. risky" customers makes it difficult to forecast monthly cash inflows, hindering financial planning and operational stability.
3.  **Lack of Data-Driven Strategy**: Decisions on who to contact and when are based on "gut feeling" rather than payment data, likely resulting in suboptimal reminder timing and tone.

## 2. Key Success Metrics
To measure the improvement in the AR process, we will track:
1.  **Days Sales Outstanding (DSO)**: The average number of days it takes to collect payment after a sale. *Goal: Reduce overall DSO.*
2.  **Collection Effectiveness Index (CEI)**: The percentage of accounts receivable collected in a given period relative to what was available to collect. *Goal: Increase CEI.*
3.  **Percentage of Overdue Receivables**: The ratio of overdue amount to total outstanding receivables. *Goal: Decrease this percentage, specifically in the >90 days bucket.*
4.  **Bad Debt Ratio**: The percentage of invoiced revenue that is written off as uncollectible. *Goal: Minimize write-offs through early identification of at-risk invoices.*
5.  **Forecast Accuracy**: Variance between predicted cash collections vs. actual collections. *Goal: <10% variance.*

## 3. Assumptions about Data & Context
*   **Data Completeness**: We assume `data.csv` represents the full picture of relevant invoices. Missing `paid_on_date` implies the invoice is either Open (outstanding) or Written Off (if very old).
*   **Dates**: We assume `issue_date`, `due_date`, and `paid_on_date` are accurate. `due_date` is the agreed payment deadline.
*   **Customer ID**: `payer_id` uniquely identifies a customer entity.
*   **Payment Behavior Stability**: We assume historical payment patterns (e.g., typically pays 5 days late) are somewhat predictive of future behavior, barring major external shocks.
*   **Write-off Threshold**: Without an explicit field, we may assume invoices overdue by a significant margin (e.g., >365 days) with no payment are effectively "Bad Debt" for analysis purposes, or we will model them as "At Risk".

## 4. Analysis Approach
1.  **Exploratory Data Analysis (EDA)**: Clean date fields, handle missing values, and compute derived features like "Days to Pay" and "Days Overdue".
2.  **Customer Segmentation**: We will segment customers based on their payment behavior (Rapid Payers, Consistent Late Payers, High Risk, etc.) rather than just invoice volume. This aligns action plans with behavior.
3.  **Collection Strategy**: Based on segments, we will propose distinct communication workflows (e.g., automated email for "Forgetful", phone call for "High Risk").
4.  **Forecasting**: We will use historical realization rates to project future cash flow, adjusting for the probability of payment derived from our risk segmentation.
