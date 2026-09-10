import json, random
from datetime import datetime, timedelta
from google.cloud import bigquery
import uuid, sys

def generate_agent_trace(agent_type, timestamp):
    agent_configs = {
        "customer_service": {
            "agent_id": "cs-agent-v1",
            "latency_range": (100, 800),
            "quality_base": 7.5,
            "hallucination_prob": 0.05,
        },
        "research": {
            "agent_id": "research-agent-v1",
            "latency_range": (500, 3000),
            "quality_base": 8.0,
            "hallucination_prob": 0.08,
        },
        "coding": {
            "agent_id": "coding-agent-v1",
            "latency_range": (200, 2000),
            "quality_base": 8.2,
            "hallucination_prob": 0.03,
        }
    }
    
    config = agent_configs[agent_type]
    latency = random.uniform(*config["latency_range"])
    success = random.random() > 0.05
    hallucination_detected = random.random() < config["hallucination_prob"]
    
    quality_score = config["quality_base"] + random.gauss(0, 0.8)
    if hallucination_detected:
        quality_score -= 2.0
    quality_score = max(1, min(10, quality_score))
    
    input_tokens = random.randint(100, 500)
    response_tokens = random.randint(200, 1000)
    total_cost = (input_tokens + response_tokens) * 0.000002
    
    return {
        "trace_id": str(uuid.uuid4()),
        "agent_id": config["agent_id"],
        "agent_type": agent_type,
        "timestamp": timestamp.isoformat(),
        "user_input": f"User query #{random.randint(1,1000)}",
        "agent_response": f"Agent response",
        "response_tokens": response_tokens,
        "input_tokens": input_tokens,
        "latency_ms": latency,
        "success": success,
        "error_message": None if success else "Error",
        "api_calls": random.randint(1, 5),
        "total_cost_usd": total_cost,
        "cost_per_token": total_cost / (input_tokens + response_tokens),
        "decision_quality_score": quality_score,
        "hallucination_detected": hallucination_detected,
        "hallucination_confidence": random.uniform(0.6, 0.99) if hallucination_detected else 0,
        "decision_reasoning": json.dumps({"step": "reasoning"}),
        "user_id": f"user_{random.randint(1000, 9999)}",
        "session_id": str(uuid.uuid4()),
        "model_used": "gemini-1.5-pro",
        "environment": "production",
    }

def main():
    client = bigquery.Client()
    project_id = client.project
    table_id = f"{project_id}.agent_monitoring.agent_traces"
    
    print(f"🚀 Generating 5000 traces...")
    traces = []
    now = datetime.utcnow()
    
    for i in range(5000):
        agent_type = random.choice(["customer_service", "research", "coding"])
        days_back = random.randint(0, 6)
        hours_back = random.randint(0, 23)
        timestamp = now - timedelta(days=days_back, hours=hours_back)
        traces.append(generate_agent_trace(agent_type, timestamp))
        
        if (i + 1) % 500 == 0:
            print(f"  ✓ {i + 1}/5000")
    
    print("⬆️ Uploading to BigQuery...")
    errors = client.insert_rows_json(table_id, traces)
    
    if not errors:
        print(f"✅ Uploaded {len(traces)} traces!")
        result = client.query(f"SELECT COUNT(*) as count FROM `{table_id}`").result()
        count = list(result)[0][0]
        print(f"✅ Verified: {count} traces in BigQuery")
        return True
    else:
        print(f"❌ Errors: {errors}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)