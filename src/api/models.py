from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    n_features: int
    timestamp: str

class ForecastRequest(BaseModel):
    product_id: int = Field(..., ge=1)
    week_index: int = Field(..., ge=0)
    features: Dict[str, float]

class ForecastResponse(BaseModel):
    product_id: int
    week_index: int
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float
    timestamp: str

class BatchForecastRequest(BaseModel):
    requests: List[ForecastRequest]

class BatchForecastResponse(BaseModel):
    forecasts: List[ForecastResponse]
    n_predictions: int
    timestamp: str

class LatestForecastResponse(BaseModel):
    product_id: int
    predicted_demand: float
    recent_avg: float
    change_pct: float
    confidence_lower: float
    confidence_upper: float

class Alert(BaseModel):
    product_id: int
    alert_type: str
    severity: str
    predicted: float
    recent_avg: float
    change_pct: float
    action: str

class AlertsResponse(BaseModel):
    alerts: List[Alert]
    n_alerts: int
    week_index: int
    timestamp: str

class ShapContribution(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: str

class ShapResponse(BaseModel):
    product_id: int
    week_index: int
    prediction: float
    base_value: float
    top_contributions: List[ShapContribution]
    timestamp: str
