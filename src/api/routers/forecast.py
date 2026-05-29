
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List
from ..models import (ForecastRequest, ForecastResponse, BatchForecastRequest,
                      BatchForecastResponse, LatestForecastResponse,
                      ShapResponse, ShapContribution)
from ..services.predictor import PredictorService

router = APIRouter(prefix='/forecast', tags=['Forecast'])
_predictor = None

def get_predictor():
    if _predictor is None:
        raise HTTPException(status_code=503, detail='Predictor not initialised')
    return _predictor

def set_predictor(p):
    global _predictor
    _predictor = p

@router.get('/latest', response_model=List[LatestForecastResponse])
async def get_latest_forecasts(predictor=Depends(get_predictor)):
    return predictor.predict_latest_week()

@router.get('/shap/{product_id}', response_model=ShapResponse)
async def get_shap(product_id: int, predictor=Depends(get_predictor)):
    prod = predictor.df[predictor.df['product_id'] == product_id]
    if len(prod) == 0:
        raise HTTPException(status_code=404, detail=f'Product {product_id} not found')
    row      = prod.iloc[-1]
    features = {f: float(row.get(f, 0)) for f in predictor.features}
    expl     = predictor.explain(features)
    return ShapResponse(product_id=product_id, week_index=int(row['week_index']),
        prediction=expl['prediction'], base_value=expl['base_value'],
        top_contributions=[ShapContribution(**c) for c in expl['top_contributions']],
        timestamp=datetime.utcnow().isoformat())

@router.get('/{product_id}', response_model=LatestForecastResponse)
async def get_product_forecast(product_id: int, predictor=Depends(get_predictor)):
    results = predictor.predict_latest_week()
    match   = [r for r in results if r['product_id'] == product_id]
    if not match:
        raise HTTPException(status_code=404, detail=f'Product {product_id} not found')
    return match[0]

@router.post('/single', response_model=ForecastResponse)
async def post_single_forecast(request: ForecastRequest, predictor=Depends(get_predictor)):
    pred, lower, upper = predictor.predict(request.features)
    return ForecastResponse(product_id=request.product_id, week_index=request.week_index,
        predicted_demand=pred, confidence_lower=lower, confidence_upper=upper,
        timestamp=datetime.utcnow().isoformat())

@router.post('/batch', response_model=BatchForecastResponse)
async def post_batch_forecast(request: BatchForecastRequest, predictor=Depends(get_predictor)):
    forecasts = []
    for req in request.requests:
        pred, lower, upper = predictor.predict(req.features)
        forecasts.append(ForecastResponse(product_id=req.product_id,
            week_index=req.week_index, predicted_demand=pred,
            confidence_lower=lower, confidence_upper=upper,
            timestamp=datetime.utcnow().isoformat()))
    return BatchForecastResponse(forecasts=forecasts, n_predictions=len(forecasts),
        timestamp=datetime.utcnow().isoformat())
