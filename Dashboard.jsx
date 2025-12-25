import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './Dashboard.css';

const API_URL = 'http://localhost:8000';

const MUMBAI_ZONES = {
  'Bandra': [19.0596, 72.8295],
  'Colaba': [18.9068, 72.8147],
  'Andheri': [19.1136, 72.8697],
  'Dadar': [19.0176, 72.8561],
  'Borivali': [19.2304, 72.8564]
};

function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_points: 0,
    anomalies: 0,
    active_alerts: 0,
    models: 5
  });
  const [zoneMarkers, setZoneMarkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const isMountedRef = useRef(true);

  // Fetch alerts with FLEXIBLE response handling
  const fetchAlerts = async () => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_URL}/alerts/active`);
      if (response.ok) {
        const data = await response.json();
        
        console.log('Alerts API Response:', data);
        
        if (isMountedRef.current) {
          // Handle both array and object responses
          let alertsArray = [];
          
          if (Array.isArray(data)) {
            alertsArray = data;
          } else if (data && typeof data === 'object') {
            if (data.alerts && Array.isArray(data.alerts)) {
              alertsArray = data.alerts;
            } else if (data.data && Array.isArray(data.data)) {
              alertsArray = data.data;
            } else {
              alertsArray = [data];
            }
          }
          
          console.log('Processed Alerts:', alertsArray);
          setAlerts(alertsArray);
          
          // AGGREGATE MARKERS BY ZONE
          const zoneAggregation = {};
          
          alertsArray.forEach(alert => {
            if (alert.affected_zones && Array.isArray(alert.affected_zones)) {
              alert.affected_zones.forEach(zone => {
                if (!zoneAggregation[zone]) {
                  zoneAggregation[zone] = {
                    zone,
                    alertCount: 0,
                    severity: alert.severity || 'low',
                    threatTypes: [],
                    confidence: 0,
                    alerts: []
                  };
                }
                zoneAggregation[zone].alertCount += 1;
                zoneAggregation[zone].confidence = Math.max(
                  zoneAggregation[zone].confidence,
                  alert.confidence || 0
                );
                if (!zoneAggregation[zone].threatTypes.includes(alert.threat_type)) {
                  zoneAggregation[zone].threatTypes.push(alert.threat_type);
                }
                if (alert.severity === 'critical') {
                  zoneAggregation[zone].severity = 'critical';
                } else if (alert.severity === 'high' && zoneAggregation[zone].severity !== 'critical') {
                  zoneAggregation[zone].severity = 'high';
                } else if (alert.severity === 'medium' && zoneAggregation[zone].severity === 'low') {
                  zoneAggregation[zone].severity = 'medium';
                }
                zoneAggregation[zone].alerts.push(alert);
              });
            }
          });
          
          const aggregatedMarkers = Object.values(zoneAggregation);
          console.log('Aggregated Zone Markers:', aggregatedMarkers);
          setZoneMarkers(aggregatedMarkers);
        }
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_URL}/stats`);
      if (response.ok) {
        const data = await response.json();
        console.log('Stats API Response:', data);
        
        setStats({
          total_points: data.data?.total_points || 0,
          anomalies: data.data?.anomalies_detected || 0,
          active_alerts: alerts.length,
          models: 5
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    setLoading(true);
    
    // Initial fetch
    fetchAlerts().then(() => setLoading(false));
    fetchStats();

    // Set up polling intervals
    const alertsInterval = setInterval(fetchAlerts, 2000);
    const statsInterval = setInterval(fetchStats, 5000);

    return () => {
      isMountedRef.current = false;
      clearInterval(alertsInterval);
      clearInterval(statsInterval);
    };
  }, []);

  // Update stats when alerts change
  useEffect(() => {
    setStats(prev => ({
      ...prev,
      active_alerts: alerts.length
    }));
  }, [alerts]);

  const anomalyPercentage = stats.total_points > 0
    ? ((stats.anomalies / stats.total_points) * 100).toFixed(1)
    : 0;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <span className="logo-icon">🛡️</span>
          <h1>Project Sentinel v3.0</h1>
          <p className="tagline">Advanced Multi-Model AI for Public Health Intelligence</p>
          <span className="system-status">● System Active</span>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>DATA POINTS</h3>
            <p className="stat-value">{stats.total_points}</p>
            <p className="stat-label">📈 Real-time monitoring</p>
          </div>
        </div>
        <div className="stat-card alert-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>ACTIVE ALERTS</h3>
            <p className="stat-value">{stats.active_alerts}</p>
            <p className="stat-label">⚠️ Threats active</p>
          </div>
        </div>
        <div className="stat-card anomaly-card">
          <div className="stat-icon">💧</div>
          <div className="stat-content">
            <h3>ANOMALIES</h3>
            <p className="stat-value">{stats.anomalies}</p>
            <p className="stat-label">{anomalyPercentage}% of total</p>
          </div>
        </div>
        <div className="stat-card model-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <h3>ML MODELS</h3>
            <p className="stat-value">{stats.models}</p>
            <p className="stat-label">Ensemble detection</p>
          </div>
        </div>
      </div>

      {/* Model Status */}
      <div className="models-status">
        <h3>⚙️ Active AI Detection Models</h3>
        <div className="models-grid">
          <div className="model-item">
            <span className="model-name">IFOREST</span>
            <span className="model-weight">25%</span>
            <span className="model-status">Unsupervised</span>
          </div>
          <div className="model-item">
            <span className="model-name">LOF</span>
            <span className="model-weight">20%</span>
            <span className="model-status">Unsupervised</span>
          </div>
          <div className="model-item">
            <span className="model-name">ECOD</span>
            <span className="model-weight">20%</span>
            <span className="model-status">Unsupervised</span>
          </div>
          <div className="model-item">
            <span className="model-name">PROPHET</span>
            <span className="model-weight">20%</span>
            <span className="model-status">Time Series</span>
          </div>
          <div className="model-item">
            <span className="model-name">ARIMA</span>
            <span className="model-weight">15%</span>
            <span className="model-status">Time Series</span>
          </div>
        </div>
        <p className="ensemble-note">🗳️ Ensemble voting: 3+ models required for alert</p>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Map Section */}
        <div className="map-section">
          <h3>🗺️ Mumbai Health Surveillance ({zoneMarkers.length} zones active)</h3>
          <MapContainer
            center={[19.0760, 72.8777]}
            zoom={11}
            style={{ height: '480px', width: '100%', borderRadius: '8px' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {zoneMarkers.map((marker, idx) => {
              const coords = MUMBAI_ZONES[marker.zone] || [19.0760, 72.8777];
              const color =
                marker.severity === 'critical'
                  ? '#dc2626'
                  : marker.severity === 'high'
                  ? '#ea580c'
                  : marker.severity === 'medium'
                  ? '#f59e0b'
                  : '#10b981';

              // Dynamic radius based on alert count
              const radius = Math.min(15 + marker.alertCount * 1.5, 30);

              return (
                <CircleMarker
                  key={`zone-${marker.zone}`}
                  center={coords}
                  radius={radius}
                  fillColor={color}
                  color={color}
                  weight={2}
                  opacity={0.8}
                  fillOpacity={0.5}
                >
                  <Popup>
                    <div style={{ minWidth: '250px', fontSize: '0.95em' }}>
                      <h4 style={{ margin: '0 0 10px 0', color: color, fontWeight: 'bold' }}>
                        {marker.zone.toUpperCase()}
                      </h4>
                      <p><strong>Total Alerts:</strong> {marker.alertCount}</p>
                      <p><strong>Severity:</strong> {marker.severity.toUpperCase()}</p>
                      <p><strong>Confidence:</strong> {marker.confidence.toFixed(1)}%</p>
                      <p><strong>Threat Types:</strong> {marker.threatTypes.map(t => t.replace(/_/g, ' ')).join(', ')}</p>
                      <hr style={{ margin: '8px 0', borderColor: 'rgba(0,0,0,0.1)' }} />
                      <p style={{ fontSize: '0.85em', color: '#666' }}>
                        {marker.alerts.length} active threat(s) in this zone
                      </p>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>

        {/* Alerts Section */}
        <div className="alerts-section">
          <h3>🚨 Active Threats ({alerts.length})</h3>
          <div className="alerts-list">
            {alerts.length === 0 ? (
              <div className="no-alerts">
                <p>✅ No active threats detected</p>
                <p className="sub-text">System monitoring normally</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div 
                  key={alert.alert_id || Math.random()} 
                  className={`alert-item severity-${alert.severity || 'low'}`}
                >
                  <div className="alert-header">
                    <span className="alert-severity">{(alert.severity || 'LOW').toUpperCase()}</span>
                    <span className="alert-confidence">{(alert.confidence || 0).toFixed(1)}%</span>
                  </div>
                  <h4>{(alert.threat_type || 'UNKNOWN').replace(/_/g, ' ').toUpperCase()}</h4>
                  <p className="alert-description">{alert.description || 'No description'}</p>
                  {alert.affected_zones && alert.affected_zones.length > 0 && (
                    <div className="alert-zones">
                      <span className="zone-label">📍 Areas:</span>
                      <span className="zone-name">{alert.affected_zones.join(', ')}</span>
                    </div>
                  )}
                  {alert.recommendations && alert.recommendations.length > 0 && (
                    <div className="alert-actions">
                      <h5>📋 Actions:</h5>
                      <ul>
                        {alert.recommendations.slice(0, 2).map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

