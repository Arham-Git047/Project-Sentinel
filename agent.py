"""
Sentinel Agent - Autonomous AI
✅ FIXED: No cooldown, threshold=3, immediate accumulation
"""

from data_models import ThreatAlert, Severity, ThreatType
from datetime import datetime, timedelta
from collections import deque, defaultdict
import uuid

class SentinelAgent:
    def __init__(self):
        """Initialize Sentinel Agent"""
        self.data_buffer = deque(maxlen=100)
        self.active_alerts = []
        self.alert_threshold = 3  # ✅ INCREASED from 2 to 3
        self.anomaly_buffer = defaultdict(list)
        self.total_alerts_generated = 0
        self.alert_expiry_hours = 24
        
        print("🛡️ Sentinel Agent initialized")
        print(f"   Alert threshold: {self.alert_threshold}+ anomalies")
        print(f"   Ensemble threshold: 3/5 models (60%)")
        print(f"   NO COOLDOWN - immediate successive alerts\n")
    
    def perceive(self, data_point: dict):
        """Perceive environment"""
        self.data_buffer.append(data_point)
        
        if data_point.get('is_anomaly', False):
            zone = data_point.get('zone_id', 'unknown')
            self.anomaly_buffer[zone].append({
                'timestamp': data_point.get('timestamp'),
                'data_type': data_point.get('data_type'),
                'value': data_point.get('value'),
                'confidence': data_point.get('confidence', 0),
                'detected_at': datetime.now()
            })
            
            if len(self.anomaly_buffer[zone]) > 100:
                self.anomaly_buffer[zone] = self.anomaly_buffer[zone][-100:]
        
        self._cleanup_expired_alerts()
    
    def reason(self) -> ThreatAlert:
        """
        ✅ FIXED: No cooldown, immediate alerts
        """
        for zone, anomalies in self.anomaly_buffer.items():
            recent_anomalies = anomalies[-10:]
            
            if len(recent_anomalies) >= self.alert_threshold:
                data_types = set(a['data_type'] for a in recent_anomalies)
                zone_values = defaultdict(list)
                
                for anomaly in recent_anomalies:
                    zone_values[anomaly['data_type']].append(anomaly['value'])
                
                threat_type = self.determine_threat_type(data_types, zone_values)
                severity = self.calculate_severity(recent_anomalies)
                avg_confidence = sum(a['confidence'] for a in recent_anomalies) / len(recent_anomalies)
                
                alert = self.generate_alert(
                    zone=zone,
                    threat_type=threat_type,
                    severity=severity,
                    confidence=avg_confidence,
                    anomalies=recent_anomalies,
                    data_types=data_types
                )
                
                # ✅ CRITICAL: Clear buffer after alert to prevent re-trigger
                self.anomaly_buffer[zone].clear()
                
                return alert
        
        return None
    
    def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        expiry_threshold = datetime.now() - timedelta(hours=self.alert_expiry_hours)
        
        initial = len(self.active_alerts)
        self.active_alerts = [
            a for a in self.active_alerts 
            if a.timestamp > expiry_threshold
        ]
        
        if len(self.active_alerts) < initial:
            print(f"   🧹 Cleaned {initial - len(self.active_alerts)} expired alerts")
    
    def determine_threat_type(self, data_types: set, zone_values: dict) -> ThreatType:
        """Determine threat type"""
        if 'water_quality' in data_types:
            water_values = zone_values.get('water_quality', [])
            if water_values:
                avg = sum(water_values) / len(water_values)
                if avg < 6.0 or avg > 9.0:
                    print(f"   💧 CRITICAL water (pH: {avg:.1f})")
                    return ThreatType.WATERBORNE
                elif avg < 7.0 or avg > 8.5:
                    print(f"   💧 Water concern (pH: {avg:.1f})")
                    return ThreatType.WATERBORNE
        
        if 'air_quality' in data_types:
            air_values = zone_values.get('air_quality', [])
            if air_values:
                avg = sum(air_values) / len(air_values)
                if avg > 150:
                    print(f"   💨 Air contamination (AQI: {avg:.0f})")
                    return ThreatType.AIRBORNE
        
        if 'pharmacy_sales' in data_types and 'hospital_visits' in data_types:
            pharmacy = zone_values.get('pharmacy_sales', [])
            hospital = zone_values.get('hospital_visits', [])
            
            if pharmacy and hospital:
                avg_p = sum(pharmacy) / len(pharmacy)
                avg_h = sum(hospital) / len(hospital)
                
                if avg_p > 180 and avg_h > 100:
                    print(f"   🍽️  Foodborne (P: {avg_p:.0f}, H: {avg_h:.0f})")
                    return ThreatType.FOODBORNE
        
        if len(data_types) >= 3:
            print(f"   🦟 Multi-source ({len(data_types)} types)")
            return ThreatType.VECTOR
        
        if 'water_quality' in data_types:
            return ThreatType.WATERBORNE
        elif 'air_quality' in data_types:
            return ThreatType.AIRBORNE
        elif 'pharmacy_sales' in data_types or 'hospital_visits' in data_types:
            return ThreatType.FOODBORNE
        
        return ThreatType.UNKNOWN
    
    def calculate_severity(self, anomalies: list) -> Severity:
        """Calculate severity"""
        avg_confidence = sum(a['confidence'] for a in anomalies) / len(anomalies)
        unique_types = len(set(a['data_type'] for a in anomalies))
        
        score = 0
        score += min(len(anomalies) / 10, 1.0) * 40
        score += (avg_confidence / 100) * 30
        score += min(unique_types / 4, 1.0) * 30
        
        if score >= 75:
            return Severity.CRITICAL
        elif score >= 60:
            return Severity.HIGH
        elif score >= 40:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def generate_alert(self, zone: str, threat_type: ThreatType, 
                      severity: Severity, confidence: float,
                      anomalies: list, data_types: set) -> ThreatAlert:
        """Generate alert"""
        alert_id = str(uuid.uuid4())
        description = self._generate_description(threat_type, zone, len(anomalies), data_types)
        recommendations = self._generate_recommendations(threat_type, severity, zone)
        
        alert = ThreatAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            threat_type=threat_type,
            severity=severity,
            confidence=round(confidence, 1),
            affected_zones=[zone],
            description=description,
            recommendations=recommendations,
            data_sources=list(data_types),
            anomaly_count=len(anomalies)
        )
        
        self.total_alerts_generated += 1
        return alert
    
    def _generate_description(self, threat_type: ThreatType, zone: str, 
                             count: int, data_types: set) -> str:
        """Generate description"""
        threat_names = {
            ThreatType.WATERBORNE: "waterborne contamination outbreak",
            ThreatType.AIRBORNE: "airborne contamination event",
            ThreatType.FOODBORNE: "foodborne illness outbreak",
            ThreatType.VECTOR: "vector-borne disease outbreak",
            ThreatType.UNKNOWN: "public health threat"
        }
        
        name = threat_names.get(threat_type, "threat")
        types = ", ".join(sorted(data_types))
        
        return (
            f"Potential {name} detected in {zone}. "
            f"AI detected {count} anomalies across {len(data_types)} indicators "
            f"({types}). Immediate investigation required."
        )
    
    def _generate_recommendations(self, threat_type: ThreatType, 
                                  severity: Severity, zone: str) -> list:
        """Generate recommendations"""
        base = [
            f"Deploy rapid response team to {zone}",
            f"Initiate epidemiological investigation",
            f"Alert health authorities"
        ]
        
        specific = {
            ThreatType.WATERBORNE: [
                "Test water supply for contamination",
                "Issue boil water advisory",
                "Close contaminated sources",
                "Distribute bottled water",
                "Monitor gastroenteritis cases"
            ],
            ThreatType.AIRBORNE: [
                "Monitor AQI in real-time",
                "Issue public advisory",
                "Recommend indoor shelter",
                "Identify pollution sources"
            ],
            ThreatType.FOODBORNE: [
                "Inspect food establishments",
                "Issue food safety alerts",
                "Test food samples",
                "Close contaminated sources"
            ],
            ThreatType.VECTOR: [
                "Deploy vector control",
                "Increase disease surveillance",
                "Issue awareness campaign",
                "Eliminate breeding sites"
            ],
            ThreatType.UNKNOWN: [
                "Conduct environmental sampling",
                "Increase surveillance",
                "Mobilize investigation team"
            ]
        }
        
        recs = base + specific.get(threat_type, [])
        
        if severity == Severity.CRITICAL:
            recs.insert(0, "⚠️ CRITICAL: Declare emergency")
        elif severity == Severity.HIGH:
            recs.insert(0, "⚠️ HIGH: Escalate immediately")
        
        return recs
    
    def act(self, alert: ThreatAlert):
        """Execute actions"""
        self.active_alerts.append(alert)
        
        print(f"\n🚨 ALERT GENERATED:")
        print(f"   ID: {alert.alert_id[:16]}...")
        print(f"   Type: {alert.threat_type.value}")
        print(f"   Severity: {alert.severity.value}")
        print(f"   Zone: {', '.join(alert.affected_zones)}")
        print(f"   Confidence: {alert.confidence}%")
        
        try:
            from notifications import notification_service
            
            alert_dict = alert.model_dump()
            
            sms = notification_service.send_alert_sms(alert_dict)
            if sms.get('success'):
                print(f"   📱 SMS sent")
                alert.notifications_sent.append("SMS")
            
            whatsapp = notification_service.send_alert_whatsapp(alert_dict)
            if whatsapp.get('success'):
                print(f"   💬 WhatsApp sent")
                alert.notifications_sent.append("WhatsApp")
        except:
            pass
    
    def get_stats(self) -> dict:
        """Get statistics"""
        return {
            "total_alerts": self.total_alerts_generated,
            "active_alerts": len(self.active_alerts),
            "data_points_processed": len(self.data_buffer),
            "active_zones": len(self.anomaly_buffer),
            "alert_threshold": self.alert_threshold
        }

# Global instance
agent = SentinelAgent()
