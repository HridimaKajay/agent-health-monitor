from google.cloud import firestore
from datetime import datetime
import sys

def init_firestore():
    print("🔥 Initializing Firestore...")
    db = firestore.Client()
    
    agents = [
        {
            "agent_id": "cs-agent-v1",
            "agent_type": "customer_service",
            "status": "active",
            "last_heartbeat": datetime.now(),
            "current_load": 0,
            "error_count_5min": 0,
            "health_status": "healthy",
            "health_score": 85.5,
            "metadata": {
                "team": "customer-support",
                "owner": "you",
                "model": "gemini-1.5-pro",
                "region": "us-central1"
            }
        },
        {
            "agent_id": "research-agent-v1",
            "agent_type": "research",
            "status": "active",
            "last_heartbeat": datetime.now(),
            "current_load": 0,
            "error_count_5min": 0,
            "health_status": "healthy",
            "health_score": 82.0,
            "metadata": {
                "team": "data-science",
                "owner": "you",
                "model": "gemini-1.5-pro",
                "region": "us-central1"
            }
        },
        {
            "agent_id": "coding-agent-v1",
            "agent_type": "coding",
            "status": "active",
            "last_heartbeat": datetime.now(),
            "current_load": 0,
            "error_count_5min": 0,
            "health_status": "healthy",
            "health_score": 88.0,
            "metadata": {
                "team": "engineering",
                "owner": "you",
                "model": "gemini-1.5-pro",
                "region": "us-central1"
            }
        }
    ]
    
    for agent in agents:
        db.collection("agents").document(agent["agent_id"]).set(agent)
        print(f"  ✅ {agent['agent_id']}")
    
    print("✅ Firestore ready!")
    return True

if __name__ == "__main__":
    success = init_firestore()
    sys.exit(0 if success else 1)