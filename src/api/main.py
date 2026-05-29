
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from .routers import forecast as forecast_module
from .routers import alerts as alerts_module
from .routers.forecast import set_predictor
from .services.predictor import PredictorService
from .models import HealthResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Starting Supply Chain API...')
    predictor = PredictorService()
    set_predictor(predictor)
    print('Model loaded - API ready')
    yield
    print('Shutting down API')

app = FastAPI(
    title='Supply Chain Planning API',
    description='XGBoost demand forecasting for manufacturing supply chain.',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:5173'],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(forecast_module.router)
app.include_router(alerts_module.router)

@app.get('/', response_model=HealthResponse, tags=['Health'])
async def health_check():
    from .routers.forecast import _predictor
    return HealthResponse(status='ok', model_loaded=_predictor is not None,
        n_features=len(_predictor.features) if _predictor else 0,
        timestamp=datetime.utcnow().isoformat())
