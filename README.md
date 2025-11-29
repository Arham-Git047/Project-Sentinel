# 🛡️ Project Sentinel

### **From Reaction to Foresight: Agentic AI for Public Health**

**Project Sentinel** is an autonomous intelligence system designed to shift public health from *Crisis Management* to *Proactive Stewardship*. By using an ensemble of unsupervised machine learning models, it detects silent precursors to disease outbreaks (like water contamination or pharmacy sales spikes) days before they overwhelm hospitals.

-----

## The Problem: The "Response Gap"

In dense urban environments like Mumbai, critical health data exists in silos.

1.  **Water Quality Sensors** detect a pH drop on Monday.
2.  **Pharmacies** see a spike in anti-diarrheal sales on Wednesday.
3.  **Hospitals** are overwhelmed by patients on Friday.

Authorities currently react on **Friday**. Project Sentinel alerts them on **Monday**.

-----

## How It Works: The "Perceive-Reason-Act" Loop

Sentinel is not just a dashboard; it is an **AI Agent** that runs on a continuous autonomous loop:

### 1\. Perceive (Data Ingestion)

The system ingests real-time streams via **FastAPI** from diverse urban nodes:

  * 💧 Water Quality Sensors (pH, Turbidity)
  * 💊 Hyper-local Pharmacy Sales (OTC trends)
  * 🏥 Hospital Admission Logs (Anonymized)
  * 💨 Environmental Sensors (AQI)

### 2\. Reason (Ensemble ML Detection)

We don't rely on simple thresholds. We use a **5-Model Ensemble** to detect statistical anomalies that a human would miss:

  * **Unsupervised Models:** Isolation Forest, Local Outlier Factor (LOF), ECOD.
  * **Time-Series Models:** Prophet, ARIMA.
  * **Consensus Logic:** An alert is only triggered if **3 out of 5 (60%)** models agree, drastically reducing false positives.

### 3\. Act (Autonomous Response)

Once a threat is verified, the Agent takes charge:

  * **Geo-Localization:** Pinpoints the "Patient Zero" zone (e.g., Bandra West).
  * **Prescription:** Generates specific containment actions (e.g., "Deploy mobile testing unit").
  * **Notification:** Bypasses bureaucracy via **Twilio API** to send WhatsApp/SMS alerts directly to field officers.

-----

## 📸 Dashboard Preview

  * **Live Map:** Real-time zoning of Mumbai (Bandra, Colaba, Andheri, Dadar) with dynamic threat radii.
  * **Command Center:** Live statistics on data points, anomaly rates, and active ML model weights.
  * **Alert Feed:** Prioritized list of active threats with confidence scores and immediate action items.

-----

## 🛠️ Tech Stack

### **Backend (Python)**

  * **FastAPI:** High-performance async API for data ingestion.
  * **PyOD (Python Outlier Detection):** The engine behind IForest, LOF, and ECOD.
  * **Twilio API:** For programmable SMS/WhatsApp alerting.
  * **NumPy/Pandas:** High-speed data manipulation.

### **Frontend (React)**

  * **Vite:** Next-gen frontend tooling.
  * **Leaflet Maps:** For geospatial visualization of Mumbai zones.
  * **CSS Modules:** For a clean, futuristic glassmorphism UI.

-----

[](https://www.google.com/search?q=https://mumbaihacks.in)
[](https://python.org)
[](https://fastapi.tiangolo.com)
[](https://react.dev)

## 🚀 Installation & Setup

### Prerequisites

  * Python 3.9+
  * Node.js & npm
  * Twilio Account (Optional, for SMS features)

### 1\. Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/project-sentinel.git
cd project-sentinel/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "TWILIO_ACCOUNT_SID=your_sid" >> .env
echo "TWILIO_AUTH_TOKEN=your_token" >> .env
echo "TWILIO_PHONE_NUMBER=your_number" >> .env

# Start the Sentinel Brain
python main.py
```

### 2\. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start the Dashboard
npm run dev
```

### 3\. run the Simulation (The Magic ✨)

To see the Agent in action, run the advanced data generator. This simulates a realistic **Waterborne Outbreak in Bandra**.

```bash
# In a new terminal window
cd backend
python generator_advanced.py
```

*Watch as the terminal simulates normal data, then injects a bio-threat, triggers the ML ensemble, and fires an alert to the dashboard instantly.*

-----

## 📂 Project Structure

```text
project-sentinel/
├── backend/
│   ├── agent.py                 # The Autonomous Brain (State Management)
│   ├── detector_advanced.py     # The ML Ensemble (PyOD + Voting Logic)
│   ├── main.py                  # FastAPI Entry Point
│   ├── notifications.py         # Twilio Integration Service
│   ├── generator_advanced.py    # Simulation Engine (Normal vs Outbreak data)
│   └── data_models.py           # Pydantic Schemas
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx    # Main Command Center UI
│   │   ├── App.jsx              # Application Logic
│   │   └── index.css            # Global Styling
└── README.md
```

-----

## 🔮 Future Roadmap

1.  **HL7/FHIR Integration:** Native support for hospital electronic health records.
2.  **LLM Integration:** Using Llama-3 to generate natural language situation reports based on the numeric anomalies.
3.  **Predictive Resource Allocation:** AI suggesting exactly how many vaccine doses to move to a specific pincode.
4.  **Data Sovereignty via Blockchain:** Zero-Knowledge Privacy: We prove outbreaks exist mathematically without ever revealing the underlying patient data.

Elastic Infrastructure: Automatically expands server capacity to handle city-wide data surges instantly.
-----

## 👥 Team

Built with ❤️ for **MumbaiHacks 2025**

  * **[Arham Kelkar]** - AI Architect & Agent Logic
  * **[Priyanshu Raj]** - Full Stack Developer (React/FastAPI)


-----

> *"The best time to stop an outbreak is before it happens."* - **Project Sentinel**
