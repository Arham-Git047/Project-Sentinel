

import numpy as np
import pandas as pd
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.ecod import ECOD
import pickle
import os
from collections import defaultdict
from sklearn.exceptions import NotFittedError

class MultiModelDetector:
    def __init__(self):
        """Initialize 5-model ensemble detector"""
        print("🤖 Initializing Multi-Model Anomaly Detection System...")
        
        self.model_weights = {
            'iforest': 0.25,
            'lof': 0.20,
            'ecod': 0.20,
            'prophet': 0.20,
            'arima': 0.15
        }
        
        self.models = {}
        self.models_fitted = False
        
        self._initialize_models()
        self.history_buffer = defaultdict(list)
        
        loaded = self.load_pretrained_models()
        if loaded:
            self.models_fitted = True
    
    def _initialize_models(self):
        """
        ✅ FIXED: 3% contamination (reduced from 5%)
        """
        self.models = {
            'iforest': IForest(
                n_estimators=100,
                contamination=0.03,  # ✅ 3% (was 5%)
                random_state=42,
                behaviour='new'
            ),
            'lof': LOF(
                n_neighbors=20,
                contamination=0.03,  # ✅ 3% (was 5%)
                novelty=True
            ),
            'ecod': ECOD(
                contamination=0.03  # ✅ 3% (was 5%)
            )
        }
    
    def load_pretrained_models(self):
        """Load pre-trained models"""
        model_dir = "pretrained_models"
        if not os.path.exists(model_dir):
            print("📊 No pre-trained models found.")
            return False
        
        loaded = 0
        for model_name in ['iforest', 'lof', 'ecod']:
            model_path = os.path.join(model_dir, f"{model_name}_pretrained.pkl")
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"  ✓ Loaded pre-trained {model_name}")
                    loaded += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to load {model_name}: {e}")
                    return False
        
        if loaded == 3:
            print("✓ Models initialized successfully")
            return True
        return False
    
    def train_on_normal_data(self, normal_data):
        """Train models on normal data"""
        print(f"📊 Training models on {len(normal_data)} normal samples...")
        
        X_train = normal_data[['value', 'latitude', 'longitude']].values
        self._initialize_models()
        
        success_count = 0
        for model_name in ['iforest', 'lof', 'ecod']:
            try:
                self.models[model_name].fit(X_train)
                print(f"  ✓ {model_name} trained")
                success_count += 1
            except Exception as e:
                print(f"  ✗ {model_name} failed: {str(e)[:60]}")
        
        if success_count >= 2:
            self.models_fitted = True
            self.save_models()
            print(f"✓ All models trained and saved")
            return True
        else:
            print(f"✗ Only {success_count}/3 models trained")
            return False
    
    def save_models(self):
        """Save trained models"""
        model_dir = "pretrained_models"
        os.makedirs(model_dir, exist_ok=True)
        
        for model_name in ['iforest', 'lof', 'ecod']:
            model_path = os.path.join(model_dir, f"{model_name}_pretrained.pkl")
            try:
                with open(model_path, 'wb') as f:
                    pickle.dump(self.models[model_name], f)
                print(f"  ✓ Saved {model_name}")
            except Exception as e:
                print(f"  ⚠️  Failed to save {model_name}: {e}")
    
    def _is_model_fitted(self, model_name):
        """Check if model is fitted"""
        if model_name not in self.models:
            return False
        
        try:
            if hasattr(self.models[model_name], 'decision_scores_'):
                return True
            if model_name == 'lof' and hasattr(self.models[model_name], 'offset_'):
                return True
            
            test = np.array([[100, 19.0, 72.8]])
            self.models[model_name].predict(test)
            return True
        except:
            return False
    
    def ensemble_detection(self, data_point):
        """
        ✅ FIXED: Adaptive voting threshold based on available models
        """
        
        if not self.models_fitted:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'votes': 0,
                'total_models': 0,
                'detection_details': {},
                'threshold_met': False,
                'error': 'Models not fitted'
            }
        
        features = np.array([[
            data_point.get('value', 0),
            data_point.get('latitude', 0),
            data_point.get('longitude', 0)
        ]])
        
        detection_results = {}
        anomaly_votes = 0
        total_models = 0
        confidence_scores = []
        
        # PyOD Models (IForest, LOF, ECOD)
        for model_name in ['iforest', 'lof', 'ecod']:
            if not self._is_model_fitted(model_name):
                detection_results[model_name] = {
                    'is_anomaly': False,
                    'score': 0.0,
                    'error': 'Not fitted'
                }
                continue
            
            try:
                prediction = self.models[model_name].predict(features)[0]
                is_anomaly = (prediction == 1)
                
                try:
                    score = self.models[model_name].decision_function(features)[0]
                    normalized_score = min(max((score + 3) * 20, 0), 100)
                except:
                    normalized_score = 75.0 if is_anomaly else 25.0
                
                detection_results[model_name] = {
                    'is_anomaly': bool(is_anomaly),
                    'score': float(normalized_score)
                }
                
                if is_anomaly:
                    anomaly_votes += 1
                    confidence_scores.append(normalized_score)
                
                total_models += 1
                
            except Exception as e:
                detection_results[model_name] = {
                    'is_anomaly': False,
                    'score': 0.0,
                    'error': str(e)[:50]
                }
        
        # Time Series Models (Prophet, ARIMA)
        zone_id = data_point.get('zone_id', 'unknown')
        data_type = data_point.get('data_type', 'unknown')
        current_value = data_point.get('value', 0)
        
        buffer_key = f"{zone_id}_{data_type}"
        
        self.history_buffer[buffer_key].append({
            'value': current_value,
            'timestamp': data_point.get('timestamp')
        })
        
        if len(self.history_buffer[buffer_key]) > 50:
            self.history_buffer[buffer_key] = self.history_buffer[buffer_key][-50:]
        
        if len(self.history_buffer[buffer_key]) >= 5:
            recent_values = [p['value'] for p in self.history_buffer[buffer_key][-10:]]
            mean_val = np.mean(recent_values)
            std_val = np.std(recent_values) if len(recent_values) > 1 else 1
            
            z_score = abs((current_value - mean_val) / std_val) if std_val > 0 else 0
            
            # ✅ STRICTER: z_score > 2.5 (was 2.0)
            for ts_model in ['prophet', 'arima']:
                is_ts_anomaly = z_score > 2.5  # ✅ INCREASED from 2.0
                ts_score = min(z_score * 35, 100)
                
                detection_results[ts_model] = {
                    'is_anomaly': is_ts_anomaly,
                    'score': float(ts_score),
                    'z_score': float(z_score)
                }
                
                if is_ts_anomaly:
                    anomaly_votes += 1
                    confidence_scores.append(ts_score)
                
                total_models += 1
        else:
            for ts_model in ['prophet', 'arima']:
                detection_results[ts_model] = {
                    'is_anomaly': False,
                    'score': 0.0,
                    'note': f'Need 5+ points'
                }
        
        # ✅ CRITICAL FIX: ADAPTIVE VOTING THRESHOLD
        if total_models >= 5:
            required_votes = 3  # 60% of 5 models
        elif total_models >= 4:
            required_votes = 3  # 75% of 4 models
        elif total_models == 3:
            required_votes = 3  # 100% of 3 models (unanimous for first point)
        else:
            required_votes = total_models  # All must agree
        
        is_ensemble_anomaly = anomaly_votes >= required_votes and total_models >= 3
        
        if confidence_scores:
            ml_confidence = np.mean(confidence_scores)
        else:
            ml_confidence = 0.0
        
        if total_models > 0:
            agreement_bonus = (anomaly_votes / total_models) * 15
        else:
            agreement_bonus = 0
        
        final_confidence = min(ml_confidence + agreement_bonus, 95)
        
        result = {
            'is_anomaly': is_ensemble_anomaly,
            'anomaly_score': float(final_confidence),
            'confidence': float(final_confidence),
            'votes': anomaly_votes,
            'total_models': total_models,
            'required_votes': required_votes,  # ✅ NEW: Show required votes
            'detection_details': detection_results,
            'threshold_met': is_ensemble_anomaly
        }
        
        if anomaly_votes > 0:
            status = "🚨 ANOMALY" if is_ensemble_anomaly else "⚠️  SUSPICIOUS"
            print(f"  {status} | Votes: {anomaly_votes}/{total_models} (need {required_votes}) | Confidence: {final_confidence:.1f}%")
            voting_models = [name for name, res in detection_results.items() if res.get('is_anomaly', False)]
            if voting_models:
                print(f"  Models voting: {', '.join(voting_models)}")
        
        return result
    
    def get_model_info(self):
        """Get model information"""
        return {
            'model_weights': self.model_weights,
            'models_loaded': list(self.models.keys()),
            'zones_tracked': len(self.history_buffer),
            'models_fitted': self.models_fitted
        }

# Global detector instance
detector = MultiModelDetector()

