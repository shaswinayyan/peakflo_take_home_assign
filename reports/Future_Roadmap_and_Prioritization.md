# Project Roadmap & Prioritization

**Author:** Business Analyst
**Status:** Post-Analysis Planning

## 1. Prioritization Philosophy
In this assignment, I consciously prioritized **completing fewer tasks well** (Deep Segmentation, Data Audit, Strategic Narrative) over **attempting all tasks partially** (ignoring data errors to rush a complex ML model).

*   **Trade-off Made**: I built a robust Heuristic Forecast instead of a fragile Deep Learning model.
*   **Trade-off Made**: I spent time on a "Data Story" web app to aid communication, rather than fine-tuning hyper-parameters.

## 2. "If I Had More Time" (Next Steps)
If this project extended for another week, here is the prioritized backlog:

### Immediate Priority (Week 1)
*   [ ] **Engineering Verification**: Meet with the Data Engineering team to investigate the 4,559 invoices where `Amount Due > Total Amount`. Is this interest? Or a bug?
*   [ ] **Forecast Granularity**: Break down the "3 Month" forecast into "Weekly" buckets to align with the weekly AR meetings.

### Medium Term (Month 1)
*   [ ] **CRM Integration Roadmap**: Design the workflow to push "Segment Tags" (e.g., *Prompt Payer*) back into Salesforce/HubSpot so Sales Reps can see them.
*   [ ] **Shadow ML Pilot**: Deploy the Random Forest model (demonstrated in `ML_Experiment_Report`) to run nightly and log predictions without acting on them.

### Long Term (Quarter 1)
*   [ ] **Self-Service Dashboard**: Migrate the Python notebook logic into a Tableau/PowerBI view for the CFO to check daily.
*   [ ] **Incentive Modeling**: Model the cost-benefit of offering a 2% discount for early payment vs the cost of capital.

## 3. Risk Register
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Data Error Confirmation** | High | High | If "Due > Total" is a bug, we over-reported bad debt by 15%. Re-run `analysis_script.py` immediately after fix. |
| **Seasonality Shock** | Medium | Medium | Q4 might behave differently than Q1. Refresh forecast parameters in Oct. |
