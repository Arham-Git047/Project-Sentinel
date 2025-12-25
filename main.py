"""
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
import uvicorn
import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError

from data_models import HealthDataPoint, ThreatAlert
from models.detector_advanced import detector
from agent import agent

try:
    from notifications import notification_service
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("ℹ️  Twilio notifications not available")

# ============================================
# LIFESPAN MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    # STARTUP
    print("\n" + "="*80)
    print("🛡️  PROJECT SENTINEL v3.0 - INITIALIZING")
    print("="*80)
    print("\n🔧 Detection Strategy: PyOD Ensemble (Option 1)")
    print("   Models: IsolationForest, LOF, ECOD + Time Series")
    print("   Threshold: 3/5 models (60% consensus - adaptive)")
    print("   Contamination: 3% (strictest detection)\n")
    
    models_fitted = False
    
    try:
        test_sample = np.array([[100, 19.0, 72.8]])
        
        try:
            detector.models['iforest'].predict(test_sample)
            detector.models['lof'].predict(test_sample)
            detector.models['ecod'].predict(test_sample)
            models_fitted = True
            print("✅ Pre-trained models loaded and validated\n")
        except Exception as e:
            print(f"⚠️  Models not fitted: {type(e).__name__}\n")
            models_fitted = False
        
        if not models_fitted:
            print("📊 Training models on synthetic baseline data...")
            print("   (This is normal on first run)\n")
            
            try:
                np.random.seed(42)
                
                training_samples = []
                
                # ✅ CRITICAL FIX: UNIFORM distribution (matches generator exactly)
                
                # Water quality: UNIFORM 6.5-8.5 (not Gaussian)
                training_samples.append(pd.DataFrame({
                    'value': np.random.uniform(6.5, 8.5, 250),  # ✅ UNIFORM
                    'latitude': np.random.uniform(18.9, 19.3, 250),
                    'longitude': np.random.uniform(72.8, 73.0, 250)
                }))
                
                # Air quality: UNIFORM 50-150 (not Gaussian)
                training_samples.append(pd.DataFrame({
                    'value': np.random.uniform(50, 150, 250),  # ✅ UNIFORM
                    'latitude': np.random.uniform(18.9, 19.3, 250),
                    'longitude': np.random.uniform(72.8, 73.0, 250)
                }))
                
                # Hospital visits: UNIFORM 30-90 (not Gaussian)
                training_samples.append(pd.DataFrame({
                    'value': np.random.uniform(30, 90, 250),  # ✅ UNIFORM
                    'latitude': np.random.uniform(18.9, 19.3, 250),
                    'longitude': np.random.uniform(72.8, 73.0, 250)
                }))
                
                # Pharmacy sales: UNIFORM 70-170 (not Gaussian)
                training_samples.append(pd.DataFrame({
                    'value': np.random.uniform(70, 170, 250),  # ✅ UNIFORM
                    'latitude': np.random.uniform(18.9, 19.3, 250),
                    'longitude': np.random.uniform(72.8, 73.0, 250)
                }))
                
                normal_data = pd.concat(training_samples, ignore_index=True)
                
                print(f"   Training set: {len(normal_data)} samples")
                print(f"   Features: value, latitude, longitude")
                print(f"   Distribution: UNIFORM (exact match with generator)\n")
                
                detector.train_on_normal_data(normal_data)
                
                try:
                    detector.models['iforest'].predict(test_sample)
                    detector.models['lof'].predict(test_sample)
                    detector.models['ecod'].predict(test_sample)
                    models_fitted = True
                    detector.models_fitted = True
                    print("\n✅ Models trained and validated successfully!\n")
                except Exception as verify_error:
                    models_fitted = False
                    print(f"\n⚠️  Verification failed: {verify_error}\n")
                    
            except Exception as train_error:
                print(f"\n❌ Training error: {train_error}\n")
                models_fitted = False
        
        print("="*80)
        if models_fitted:
            print("✅ ALL SYSTEMS OPERATIONAL")
        else:
            print("⚠️  SYSTEM STARTED (Models need troubleshooting)")
        print("="*80)
        print(f"   • Models fitted: {models_fitted}")
        print(f"   • Ensemble: 3/5 models (adaptive voting)")
        print(f"   • Contamination: 3% (strictest)")
        print(f"   • API docs: http://localhost:8000/docs")
        print("="*80 + "\n")
        
    except Exception as startup_error:
        print(f"\n❌ Startup error: {startup_error}\n")
    
    yield
    
    # SHUTDOWN
    try:
        print("\n" + "="*80)
        print("🛡️  SENTINEL SHUTTING DOWN")
        print("="*80)
        print(f"   • Alerts: {len(agent.active_alerts)}")
        print(f"   • Data points: {len(agent.data_buffer)}")
        print("="*80 + "\n")
    except:
        print("\n🛡️  Shutting down...\n")

# ============================================
# INITIALIZE FASTAPI
# ============================================

app = FastAPI(
    title="Project Sentinel API v3.0",
    description="Advanced Multi-Model AI for Public Health Intelligence",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Status"])
def root():
    """Root endpoint"""
    return {
        "status": "Sentinel Active",
        "version": "3.0.0",
        "strategy": "PyOD Ensemble - 3/5 models (adaptive voting)",
        "contamination": "3% (strictest)",
        "distribution": "UNIFORM (exact match)",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ingest": "/data/ingest",
            "alerts": "/alerts/active"
        }
    }

@app.get("/health", tags=["Status"])
def health_check():
    """Health check"""
    try:
        return {
            "status": "healthy" if detector.models_fitted else "degraded",
            "timestamp": datetime.now().isoformat(),
            "models": {
                "fitted": detector.models_fitted,
                "threshold": "3/5 models (adaptive)",
                "contamination": "3%",
                "distribution": "UNIFORM"
            },
            "agent": {
                "alerts": len(agent.active_alerts),
                "data_points": len(agent.data_buffer)
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/data/ingest", tags=["Data"])
def ingest_data(data: HealthDataPoint):
    """Ingest health data and detect anomalies"""
    try:
        data_dict = data.model_dump()
        
        detection_result = detector.ensemble_detection(data_dict)
        data_dict.update(detection_result)
        
        agent.perceive(data_dict)
        alert = agent.reason()
        
        alert_data = None
        if alert:
            agent.act(alert)
            alert_data = {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "threat_type": alert.threat_type.value,
                "confidence": alert.confidence,
                "affected_zones": alert.affected_zones,
                "description": alert.description,
                "recommendations": alert.recommendations[:5]
            }
        
        return {
            "received": True,
            "timestamp": data_dict.get('timestamp'),
            "zone_id": data_dict.get('zone_id'),
            "data_type": data_dict.get('data_type'),
            "value": data_dict.get('value'),
            "anomaly_detected": detection_result.get('is_anomaly'),
            "confidence": detection_result.get('confidence'),
            "ensemble_votes": f"{detection_result.get('votes')}/{detection_result.get('total_models')}",
            "detection_details": detection_result.get('detection_details'),
            "alert_generated": alert is not None,
            "alert": alert_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/data/stream", tags=["Data"])
def get_data_stream(limit: int = 50):
    """Get recent data points"""
    return {
        "total_points": len(agent.data_buffer),
        "data": list(agent.data_buffer)[-limit:]
    }

@app.get("/alerts/active", tags=["Alerts"])
def get_active_alerts():
    """Get active alerts"""
    return [alert.model_dump() for alert in agent.active_alerts]

@app.get("/alerts/{alert_id}", tags=["Alerts"])
def get_alert(alert_id: str):
    """Get specific alert"""
    for alert in agent.active_alerts:
        if alert.alert_id == alert_id:
            return alert.model_dump()
    raise HTTPException(status_code=404, detail="Alert not found")

@app.delete("/alerts/{alert_id}", tags=["Alerts"])
def dismiss_alert(alert_id: str):
    """Dismiss alert"""
    for i, alert in enumerate(agent.active_alerts):
        if alert.alert_id == alert_id:
            dismissed = agent.active_alerts.pop(i)
            return {"dismissed": True, "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/models/info", tags=["Models"])
def get_model_info():
    """Get model information"""
    model_info = detector.get_model_info()
    
    return {
        "strategy": "PyOD Ensemble (Option 1)",
        "ensemble_models": 5,
        "model_weights": model_info['model_weights'],
        "models_fitted": model_info['models_fitted'],
        "unsupervised_models": [
            "IsolationForest (25%)",
            "LOF (20%)",
            "ECOD (20%)"
        ],
        "time_series_models": [
            "Prophet (20%)",
            "AutoARIMA (15%)"
        ],
        "threshold": "3/5 models (adaptive voting)",
        "contamination": "3% (strictest)",
        "distribution": "UNIFORM (exact match)",
        "zones_tracked": model_info['zones_tracked']
    }

@app.get("/stats", tags=["Analytics"])
def get_statistics():
    """Get system statistics"""
    agent_stats = agent.get_stats()
    total_points = len(agent.data_buffer)
    anomalies = sum(1 for p in agent.data_buffer if p.get('is_anomaly', False))
    
    return {
        "system": {
            "version": "3.0.0",
            "models_fitted": detector.models_fitted,
            "strategy": "3/5 models (adaptive)",
            "contamination": "3%"
        },
        "data": {
            "total_points": total_points,
            "anomalies_detected": anomalies,
            "anomaly_rate": f"{(anomalies/total_points*100):.1f}%" if total_points > 0 else "0%"
        },
        "alerts": {
            "total_generated": agent_stats["total_alerts"],
            "currently_active": len(agent.active_alerts)
        },
        "zones": {
            "tracked": agent_stats["active_zones"]
        }
    }

@app.get("/debug/last-detection", tags=["Debug"])
def get_last_detection():
    """Debug: Last detection"""
    if len(agent.data_buffer) > 0:
        last = list(agent.data_buffer)[-1]
        return {
            "data": last,
            "is_anomaly": last.get('is_anomaly', False),
            "votes": f"{last.get('votes', 0)}/{last.get('total_models', 5)}"
        }
    return {"message": "No data yet"}

if __name__ == "__main__":
    print("\n🚀 Starting Project Sentinel v3.0...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

