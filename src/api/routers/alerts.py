
from fastapi import APIRouter, Depends, Query
from datetime import datetime
from ..models import AlertsResponse, Alert
from ..services.predictor import PredictorService
from .forecast import get_predictor

router = APIRouter(prefix='/alerts', tags=['Alerts'])

@router.get('', response_model=AlertsResponse)
async def get_alerts(severity: str = Query(default=None), predictor=Depends(get_predictor)):
    alerts_raw, week_idx = predictor.generate_alerts()
    if severity:
        alerts_raw = [a for a in alerts_raw if a['severity'] == severity.upper()]
    return AlertsResponse(alerts=[Alert(**a) for a in alerts_raw],
        n_alerts=len(alerts_raw), week_index=week_idx,
        timestamp=datetime.utcnow().isoformat())

@router.get('/summary')
async def get_summary(predictor=Depends(get_predictor)):
    alerts_raw, week_idx = predictor.generate_alerts()
    return {'week_index': week_idx, 'total_alerts': len(alerts_raw),
        'by_type': {
            'DEMAND_SPIKE': sum(1 for a in alerts_raw if a['alert_type']=='DEMAND_SPIKE'),
            'DEMAND_DROP':  sum(1 for a in alerts_raw if a['alert_type']=='DEMAND_DROP'),
            'SUPPLY_RISK':  sum(1 for a in alerts_raw if a['alert_type']=='SUPPLY_RISK'),
        },
        'by_severity': {
            'HIGH':   sum(1 for a in alerts_raw if a['severity']=='HIGH'),
            'MEDIUM': sum(1 for a in alerts_raw if a['severity']=='MEDIUM'),
        },
        'timestamp': datetime.utcnow().isoformat()}
