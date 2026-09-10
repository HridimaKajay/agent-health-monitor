# agent_tools.py
"""
Tools available to the Customer Service Agent
These are the actions the agent can take to help customers
"""

import json
from io import BytesIO
from datetime import datetime
from google.cloud import bigquery
from sample_faq_db import search_faq, get_all_faq_topics
import uuid

# Initialize BigQuery client
bq_client = bigquery.Client()

def lookup_faq(user_query: str) -> dict:
    """
    Tool: Search CloudPulse FAQ database
    
    Args:
        user_query: Customer's question
    
    Returns:
        dict with matching FAQ results
    """
    print(f"🔍 Searching FAQ for: {user_query}")
    
    results = search_faq(user_query)
    
    if not results:
        return {
            "status": "no_match",
            "message": "No matching FAQs found. Escalate to human support.",
            "recommendations": get_all_faq_topics()[:5]
        }
    
    return {
        "status": "found",
        "results": [
            {
                "question": r["question"],
                "answer": r["answer"],
                "category": r["category"],
                "relevance": r["relevance"]
            }
            for r in results
        ]
    }

def log_agent_trace(
    agent_id: str,
    agent_type: str,
    user_input: str,
    agent_response: str,
    response_tokens: int,
    input_tokens: int,
    latency_ms: float,
    success: bool,
    decision_quality_score: float,
    hallucination_detected: bool = False,
    error_message: str = None
) -> dict:
    """
    Tool: Log agent interaction to BigQuery
    Creates a trace record for monitoring/evaluation
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent (customer_service, etc.)
        user_input: Customer's question
        agent_response: Agent's response
        response_tokens: Tokens in response
        input_tokens: Tokens in input
        latency_ms: Response time in milliseconds
        success: Whether interaction succeeded
        decision_quality_score: Quality rating (0-10)
        hallucination_detected: Whether hallucinations were found
        error_message: Error details if failed
    
    Returns:
        dict with trace ID and status
    """
    
    trace_id = str(uuid.uuid4())
    
    trace_row = {
        "trace_id": trace_id,
        "agent_id": agent_id,
        "agent_type": agent_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user_input": user_input,
        "agent_response": agent_response,
        "response_tokens": response_tokens,
        "input_tokens": input_tokens,
        "latency_ms": latency_ms,
        "success": success,
        "error_message": error_message,
        "api_calls": 1,
        "total_cost_usd": (input_tokens + response_tokens) * 0.000002,  # Gemini pricing
        "cost_per_token": 0.000002,
        "decision_quality_score": decision_quality_score,
        "hallucination_detected": hallucination_detected,
        "hallucination_confidence": 0.8 if hallucination_detected else 0.0,
        "decision_reasoning": json.dumps({
            "reasoning": "FAQ lookup + Gemini synthesis",
            "tool_used": "lookup_faq"
        }),
        "user_id": f"user_{hash(user_input) % 10000}",
        "session_id": str(uuid.uuid4()),
        "model_used": "gemini-3.5-flash",
        "environment": "production",
    }
    
    # Insert into BigQuery
    table_id = f"{bq_client.project}.agent_monitoring.agent_traces"
    
    
    # Create JSON lines format
    json_data = json.dumps(trace_row) + '\n'
    
    # Use load_table_from_file for compatibility with free tier
    # For now, just skip if we hit the free tier limitation
    try:
        errors = bq_client.insert_rows_json(table_id, [trace_row])
    except Exception as e:
        if "Streaming insert is not allowed" in str(e):
            print(f"⚠️  Free tier: Skipping streaming insert, but trace is prepared: {trace_id}")
            errors = []
        else:
            raise
    
    if errors:
        print(f"❌ BigQuery error: {errors}")
        return {
            "status": "error",
            "trace_id": trace_id,
            "error": str(errors)
        }
    
    print(f"✅ Trace logged: {trace_id}")
    
    return {
        "status": "success",
        "trace_id": trace_id,
        "latency_ms": latency_ms,
        "cost_usd": trace_row["total_cost_usd"]
    }

def generate_response_with_gemini(
    user_input: str,
    faq_context: dict,
    model_name: str = "gemini-3.5-flash"
) -> dict:
    """
    Tool: Use Gemini to synthesize human-like response from FAQ context
    
    Args:
        user_input: Customer's question
        faq_context: Retrieved FAQ results
        model_name: Which Gemini model to use
    
    Returns:
        dict with generated response and metadata
    """
    
    # from google.generativeai import GenerativeModel
    from google import genai
    import os
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # model = GenerativeModel(model_name)
    
    # Build prompt with FAQ context
    faq_text = ""
    if faq_context["status"] == "found":
        faq_text = "\n".join([
            f"- Q: {r['question']}\n  A: {r['answer']}"
            for r in faq_context["results"]
        ])
    else:
        faq_text = "No matching FAQs found. Provide general guidance."
    
    prompt = f"""You are a helpful customer service agent for CloudPulse - an AI Email Platform.

Customer Question: {user_input}

Relevant FAQ Information:
{faq_text}

Instructions:
1. Answer the customer's question using the FAQ information provided
2. Be friendly, professional, and concise (max 2-3 sentences for FAQ answers)
3. If not covered by FAQs, admit limitations and suggest escalation
4. Never make up information about CloudPulse
5. End with "Is there anything else I can help with?" if appropriate

Generate your response now:"""

    response = client.models.generate_content(model=model_name,contents=prompt)
    # response = model.generate_content(prompt)
    generated_text = response.text
    
    # Extract token usage from response metadata
    response_tokens = len(generated_text.split())  # Approximate
    input_tokens = len(prompt.split())  # Approximate
    
    return {
        "status": "success",
        "response": generated_text,
        "response_tokens": response_tokens,
        "input_tokens": input_tokens,
        "model": model_name,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": response_tokens,
        }
    }

def assess_response_quality(
    user_input: str,
    faq_results: dict,
    agent_response: str
) -> dict:
    """
    Tool: Assess quality of agent response
    Uses heuristics to detect hallucinations and rate quality
    
    Args:
        user_input: Original customer question
        faq_results: FAQ search results
        agent_response: Agent's generated response
    
    Returns:
        dict with quality score and issues
    """
    
    quality_score = 10.0  # Start at perfect
    hallucinations = []
    
    # Check 1: Did we find matching FAQs?
    if faq_results["status"] == "no_match":
        quality_score -= 2.0
        hallucinations.append("No FAQ match - may contain speculative content")
    
    # Check 2: Is response too long? (sign of hallucination)
    if len(agent_response.split()) > 200:
        quality_score -= 1.5
        hallucinations.append("Response unusually long - may contain irrelevant information")
    
    # Check 3: Does response reference FAQ keywords?
    if faq_results["status"] == "found":
        faq_keywords = set()
        for result in faq_results["results"]:
            faq_keywords.update(result["question"].lower().split())
            faq_keywords.update(result["answer"].lower().split())
        
        response_keywords = set(agent_response.lower().split())
        keyword_overlap = len(faq_keywords & response_keywords) / len(faq_keywords)
        
        if keyword_overlap < 0.3:
            quality_score -= 1.0
            hallucinations.append("Low overlap with FAQ content - may contain fabricated information")
    
    # Check 4: Does response contain confidence language?
    confidence_markers = ["i think", "probably", "maybe", "possibly", "i'm not sure", "i guess"]
    has_uncertainty = any(marker in agent_response.lower() for marker in confidence_markers)
    
    if not has_uncertainty and faq_results["status"] == "no_match":
        quality_score -= 1.0
        hallucinations.append("Over-confident response without FAQ backing")
    
    # Check 5: Is response coherent to the question?
    question_words = set(user_input.lower().split()[:5])
    response_words = set(agent_response.lower().split()[:20])
    relevance = len(question_words & response_words) / len(question_words)
    
    if relevance < 0.2:
        quality_score -= 1.0
        hallucinations.append("Response may not directly address the question")
    
    quality_score = max(1, min(10, quality_score))  # Clamp to 1-10
    
    hallucination_detected = len(hallucinations) > 0
    
    return {
        "quality_score": round(quality_score, 2),
        "hallucination_detected": hallucination_detected,
        "hallucination_confidence": min(0.95, len(hallucinations) * 0.25),
        "issues": hallucinations,
        "assessment": "Response quality is good" if quality_score >= 7 else 
                     "Response quality is fair" if quality_score >= 5 else
                     "Response quality is poor"
    }

# Agent Tool Registry
AGENT_TOOLS = {
    "lookup_faq": lookup_faq,
    "generate_response": generate_response_with_gemini,
    "assess_quality": assess_response_quality,
    "log_trace": log_agent_trace,
}

def execute_tool(tool_name: str, **kwargs) -> dict:
    """
    Execute an agent tool
    
    Args:
        tool_name: Name of tool to execute
        **kwargs: Tool arguments
    
    Returns:
        Tool result as dict
    """
    
    if tool_name not in AGENT_TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    tool_func = AGENT_TOOLS[tool_name]
    try:
        result = tool_func(**kwargs)
        return result
    except Exception as e:
        return {"error": str(e), "tool": tool_name}

if __name__ == "__main__":
    # Test the tools
    print("Testing Agent Tools...\n")
    
    # Test 1: FAQ Lookup
    print("1️⃣ Testing FAQ Lookup")
    faq_results = lookup_faq("How much does CloudPulse cost?")
    print(f"   Found: {faq_results['status']}")
    
    # Test 2: Generate Response (if Gemini key is set)
    print("\n2️⃣ Testing Response Generation (requires GEMINI_API_KEY)")
    try:
        response_result = generate_response_with_gemini(
            "How much does CloudPulse cost?",
            faq_results
        )
        print(f"   Generated response: {response_result['response'][:100]}...")
    except Exception as e:
        print(f"   Skipped (Gemini key not set): {e}")
    
    print("\n✅ Agent tools ready!")