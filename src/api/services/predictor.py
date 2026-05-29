
import pickle, json, os
import numpy as np
import pandas as pd
import shap
from datetime import datetime
from typing import Dict, List, Tuple

class PredictorService:
    def __init__(self,
                 model_path='models/xgb_demand_model.pkl',
                 features_path='data/processed/feature_list.json',
                 dataset_path='data/processed/ml_dataset.csv'):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f'Model not found at {model_path}. Run Notebook 03 first.')
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(features_path) as f:
            meta = json.load(f)
        self.features = meta['features']
        self.target   = meta['target']
        self.df       = pd.read_csv(dataset_path)
        self._explainer = None
        print(f'PredictorService ready - {len(self.features)} features')

    def predict(self, features: Dict[str, float]) -> Tuple[float, float, float]:
        import pandas as pd, numpy as np
        X    = pd.DataFrame([features])[self.features].fillna(0)
        pred = float(np.maximum(self.model.predict(X)[0], 0))
        return round(pred, 1), round(pred * 0.80, 1), round(pred * 1.20, 1)

    def predict_latest_week(self) -> List[Dict]:
        import numpy as np
        last_week = self.df['week_index'].max()
        latest    = self.df[self.df['week_index'] == last_week].copy()
        X         = latest[self.features].fillna(0)
        preds     = np.maximum(self.model.predict(X), 0)
        lag_cols  = [c for c in self.features if 'ordered_qty_lag_' in c
                     and int(c.split('_')[-1]) <= 4]
        results = []
        for i, (_, row) in enumerate(latest.iterrows()):
            pred       = float(preds[i])
            recent_avg = float(latest[lag_cols].iloc[i].mean()) if lag_cols else pred
            change_pct = (pred - recent_avg) / max(recent_avg, 1) * 100
            results.append({
                'product_id':       int(row['product_id']),
                'predicted_demand': round(pred, 1),
                'recent_avg':       round(recent_avg, 1),
                'change_pct':       round(change_pct, 1),
                'confidence_lower': round(pred * 0.80, 1),
                'confidence_upper': round(pred * 1.20, 1),
            })
        return results

    def explain(self, features: Dict[str, float], top_n: int = 10) -> Dict:
        import pandas as pd, numpy as np, shap
        if self._explainer is None:
            bg = self.df[self.features].fillna(0).sample(min(100, len(self.df)), random_state=42)
            self._explainer = shap.TreeExplainer(self.model, bg)
        X          = pd.DataFrame([features])[self.features].fillna(0)
        shap_vals  = self._explainer.shap_values(X)[0]
        base_value = float(self._explainer.expected_value)
        prediction = float(np.maximum(self.model.predict(X)[0], 0))
        contribs   = sorted(
            [{'feature': f, 'value': float(features.get(f, 0)),
              'shap_value': float(s), 'direction': 'UP' if s > 0 else 'DOWN'}
             for f, s in zip(self.features, shap_vals)],
            key=lambda x: abs(x['shap_value']), reverse=True)
        return {'prediction': round(prediction,1), 'base_value': round(base_value,1),
                'top_contributions': contribs[:top_n]}

    def generate_alerts(self) -> Tuple[List[Dict], int]:
        predictions = self.predict_latest_week()
        last_week   = int(self.df['week_index'].max())
        alerts = []
        for p in predictions:
            pred   = p['predicted_demand']
            recent = p['recent_avg']
            ratio  = pred / max(recent, 1)
            pid    = p['product_id']
            prod   = self.df[self.df['product_id'] == pid]
            risk   = float(prod['supply_risk_score'].iloc[-1]) if 'supply_risk_score' in prod.columns else 0.0
            if ratio > 1.30:
                alerts.append({'product_id': pid, 'alert_type': 'DEMAND_SPIKE',
                    'severity': 'HIGH' if ratio > 1.50 else 'MEDIUM',
                    'predicted': round(pred,1), 'recent_avg': round(recent,1),
                    'change_pct': round((ratio-1)*100,1),
                    'action': 'Increase production order / draw from safety stock'})
            elif ratio < 0.70:
                alerts.append({'product_id': pid, 'alert_type': 'DEMAND_DROP',
                    'severity': 'MEDIUM', 'predicted': round(pred,1),
                    'recent_avg': round(recent,1), 'change_pct': round((ratio-1)*100,1),
                    'action': 'Reduce production order / avoid overstock'})
            if risk > 0.6 and ratio >= 0.9:
                alerts.append({'product_id': pid, 'alert_type': 'SUPPLY_RISK',
                    'severity': 'HIGH', 'predicted': round(pred,1),
                    'recent_avg': round(recent,1), 'change_pct': round((ratio-1)*100,1),
                    'action': f'Supply risk={risk:.2f} - contact supplier proactively'})
        return alerts, last_week
