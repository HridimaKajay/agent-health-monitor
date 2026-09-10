from google.cloud import bigquery
import sys

def create_schema():
    """Create BigQuery dataset and tables"""
    
    client = bigquery.Client()
    project_id = client.project
    
    print(f"📊 Creating schema in {project_id}")
    
    # Create dataset
    dataset = bigquery.Dataset(f"{project_id}.agent_monitoring")
    dataset.location = "US"
    dataset = client.create_dataset(dataset, exists_ok=True)
    print("✅ Dataset created")
    
    # Create traces table
    traces_schema = [
        bigquery.SchemaField("trace_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("agent_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("agent_type", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("user_input", "STRING"),
        bigquery.SchemaField("agent_response", "STRING"),
        bigquery.SchemaField("response_tokens", "INTEGER"),
        bigquery.SchemaField("input_tokens", "INTEGER"),
        bigquery.SchemaField("latency_ms", "FLOAT64"),
        bigquery.SchemaField("success", "BOOLEAN"),
        bigquery.SchemaField("error_message", "STRING"),
        bigquery.SchemaField("api_calls", "INTEGER"),
        bigquery.SchemaField("total_cost_usd", "FLOAT64"),
        bigquery.SchemaField("cost_per_token", "FLOAT64"),
        bigquery.SchemaField("decision_quality_score", "FLOAT64"),
        bigquery.SchemaField("hallucination_detected", "BOOLEAN"),
        bigquery.SchemaField("hallucination_confidence", "FLOAT64"),
        bigquery.SchemaField("decision_reasoning", "JSON"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("session_id", "STRING"),
        bigquery.SchemaField("model_used", "STRING"),
        bigquery.SchemaField("environment", "STRING"),
    ]
    
    table = bigquery.Table(f"{project_id}.agent_monitoring.agent_traces", schema=traces_schema)
    table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="timestamp")
    table.clustering_fields = ["agent_id", "agent_type"]
    client.create_table(table, exists_ok=True)
    print("✅ agent_traces table created")
    
    # Create metrics table
    metrics_schema = [
        bigquery.SchemaField("metric_hour", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("agent_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_requests", "INTEGER"),
        bigquery.SchemaField("successful_requests", "INTEGER"),
        bigquery.SchemaField("failed_requests", "INTEGER"),
        bigquery.SchemaField("success_rate", "FLOAT64"),
        bigquery.SchemaField("avg_latency_ms", "FLOAT64"),
        bigquery.SchemaField("p50_latency_ms", "FLOAT64"),
        bigquery.SchemaField("p95_latency_ms", "FLOAT64"),
        bigquery.SchemaField("p99_latency_ms", "FLOAT64"),
        bigquery.SchemaField("avg_quality_score", "FLOAT64"),
        bigquery.SchemaField("hallucination_count", "INTEGER"),
        bigquery.SchemaField("hallucination_rate", "FLOAT64"),
        bigquery.SchemaField("total_cost_usd", "FLOAT64"),
        bigquery.SchemaField("avg_cost_per_request", "FLOAT64"),
        bigquery.SchemaField("health_score", "FLOAT64"),
        bigquery.SchemaField("health_status", "STRING"),
    ]
    
    table = bigquery.Table(f"{project_id}.agent_monitoring.agent_metrics_hourly", schema=metrics_schema)
    table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="metric_hour")
    table.clustering_fields = ["agent_id"]
    client.create_table(table, exists_ok=True)
    print("✅ agent_metrics_hourly table created")
    
    return True

if __name__ == "__main__":
    success = create_schema()
    sys.exit(0 if success else 1)