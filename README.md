# AI Agent Health Monitor

Production-grade observability platform for multi-agent AI systems.

## 🎯 Project Status
🚧 **Work in Progress** - Week 1/3 of Patchamomma 2026

## 📋 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud SDK
- GCP Free Trial ($300 credit)

### Setup
```bash
# 1. Clone repo (or download)
cd ~/projects/agent-health-monitor

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create BigQuery schema
python data/create_bigquery_schema.py

# 5. Generate synthetic data
python data/generate_synthetic_traces.py


# 6. Initialize Firestore
python data/init_firestore.py
```

## 🏗️ Architecture


## 📊 Tech Stack
- **BigQuery**: Agent trace storage & analysis
- **Firestore**: Real-time agent state
- **Cloud Run**: Evaluation engine
- **Pub/Sub**: Message streaming
- **Gemini API**: Decision quality assessment
- **Data Studio**: Interactive dashboard

## 📝 Checkpoints
- [ ] Aug 20: Architecture + Data (Week 1)
- [ ] Aug 28: Core Engine Working (Week 2)
- [ ] Sep 5: Full Deployment (Week 3)

## 🔗 Links
- [Technical Doc](docs/ARCHITECTURE.md)
- [GCP Console](https://console.cloud.google.com)
- [Discord Community](https://discord.gg/fgHGJb3R3)

## 📄 License
MIT