import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "agent-health-monitor")
REGION = os.getenv("REGION", "us-central1")
BQ_DATASET = os.getenv("BQ_DATASET", "agent_monitoring")
BQ_TRACES_TABLE = os.getenv("BQ_TRACES_TABLE", "agent_traces")
BQ_METRICS_TABLE = os.getenv("BQ_METRICS_TABLE", "agent_metrics_hourly")
FIRESTORE_DATABASE = os.getenv("FIRESTORE_DATABASE", "(default)")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
SERVICE_NAME = os.getenv("SERVICE_NAME", "agent-health-monitor")
SERVICE_REGION = os.getenv("SERVICE_REGION", "us-central1")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")