from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import numpy as np

class Invoice(BaseModel):
    """
    Represents a single invoice record with rigorous validation.
    """
    id: str
    total_amount: float = Field(..., ge=0, description="Total value of the invoice")
    amount_due: float = Field(..., ge=0, description="Amount currently outstanding")
    issue_date: datetime
    due_date: datetime
    paid_on_date: Optional[datetime] = None
    payer_id: str

    @field_validator('total_amount', 'amount_due', mode='before')
    def parse_float(cls, v):
        if isinstance(v, str):
            # Handle potential currency symbols or empty strings if any
            clean_v = v.replace(',', '').strip()
            return float(clean_v) if clean_v else 0.0
        return v

    @field_validator('issue_date', 'due_date', 'paid_on_date', mode='before')
    def parse_date(cls, v):
        # Handle pandas NaT or None
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return None
        # If it's already a datetime (from pandas timestamp), return it
        if isinstance(v, datetime):
            return v
        # Try string parsing if needed (though pandas usually handles this)
        try:
            return datetime.fromisoformat(str(v).replace('Z', '+00:00'))
        except ValueError:
             # Fallback for common formats if ISO fails
            return v
            
    @field_validator('paid_on_date')
    def validate_payment_logic(cls, v, info):
        # We can add cross-field logic here if needed via model_validator
        # For now, just ensuring it's a valid date or None is handled by type hint
        return v
