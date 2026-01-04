# Strategic Decision: Heuristics vs. Machine Learning

**Status:** Decision Made
**Chosen Approach:** Probabilistic Heuristics (Rule-Based)

## 1. Typical vs. Specific Context
In a vacuum, Machine Learning (ML) is superior for prediction. However, in the context of **AR Operations for a CFO**, accuracy is not the only metric. Trust and "explainability" are paramount.

## 2. Why We Chose Heuristics (Probabilistic Rules)
We selected the Probabilistic bucket approach (e.g., "If <30 days late, 80% chance to collect") over our Random Forest model for the following reasons:

### A. The "Black Box" Problem in Finance
*   **Heuristics**: "We predict this will be paid because the customer historically pays 2 weeks late." -> **CFO nods.**
*   **ML Model**: "We predict this will be paid because Feature X (Log of Total Amount) combined with Feature Y (Month Index) crossed threshold Z." -> **CFO asks "Why?"**
*   **Impact**: If the ML model is wrong (which it is 13% of the time), the finance team loses trust entirely. If a rule is wrong, they understand *why* (statistical outlier) and can adjust the rule.

### B. Data Quality Risks
*   **Finding**: Our audit revealed 25% of invoices have `Amount Due > Total Amount` (likely penalties/errors).
*   **Risk**: ML models are sensitive to "garbage in". If training data contains erroneous penalty figures, the model learns noise.
*   **Resilience**: Heuristics are robust. A segment logic based on *Count* of late invoices is immune to *Amount* errors.

### C. Operational "Cold Start"
*   **Context**: For new customers, the ML model has zero history and relies on "similar" features (Invoice Size).
*   **Heuristics**: We can firmly categorize them as "New/Unknown" and apply a conservative 50% collection probability, respecting the risk of the unknown.

## 3. Evidence of Preference
*   **Interpretability**: 100% (Heuristic) vs 10% (ML).
*   **Feature Engineering Effort**: Very Low (Heuristic) vs High (ML).
*   **Maintenance**: Admin-configurable (Heuristic) vs Data Scientist required (ML).

## 4. Recommendation for Future State
We recommend running the **ML Model in "Shadow Mode"** for Q3.
1.  Use Heuristics for official forecast.
2.  Run ML predictions silently in the background.
3.  Compare both against actuals in Q4.
4.  *Only* switch if ML outperforms Heuristics by >15% consistently for 3 months.
