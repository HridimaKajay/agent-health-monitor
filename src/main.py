from flask import Flask, jsonify, request
from google.cloud import firestore
from datetime import datetime
import os
import sys

# Import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from customer_service_agent import CustomerServiceAgent

app = Flask(__name__)
fs_client = firestore.Client()
project_id = os.environ.get("GCP_PROJECT", "agent-health-monitor")

# Initialize agent
try:
    cs_agent = CustomerServiceAgent(agent_id="cs-agent-v1")
    AGENT_READY = True
except Exception as e:
    print(f"⚠️  Agent initialization warning: {e}")
    AGENT_READY = False

# ============================================================================
# HEALTH CHECK & STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "agent-health-monitor",
        "agent_ready": AGENT_READY,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    return jsonify({
        "service": "AI Agent Health Monitor",
        "version": "1.0.0",
        "agent_id": "cs-agent-v1",
        "agent_type": "customer_service",
        "status": "active" if AGENT_READY else "degraded",
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@app.route('/agent/query', methods=['POST'])
def agent_query():
    """
    Main agent endpoint
    POST body: {"question": "Your question here"}
    Returns: agent response + quality score + trace ID
    """
    
    if not AGENT_READY:
        return jsonify({
            "error": "Agent not initialized",
            "status": "error"
        }), 503
    
    try:
        data = request.json
        user_input = data.get("question", "").strip()
        
        if not user_input:
            return jsonify({
                "error": "Missing 'question' field in request",
                "status": "error"
            }), 400
        
        # Process inquiry
        result = cs_agent.process_customer_inquiry(user_input)
        
        return jsonify({
            "status": "success",
            "response": result["agent_response"],
            "quality_score": result["quality_score"],
            "hallucination_detected": result["hallucination_detected"],
            "faq_matched": result["faq_matched"],
            "latency_ms": result["latency_ms"],
            "cost_usd": result["cost_usd"],
            "trace_id": result["trace_id"],
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/agent/batch-test', methods=['POST'])
def batch_test():
    """
    Run batch test with multiple questions
    POST body: {"questions": ["Q1", "Q2", ...]}
    """
    
    if not AGENT_READY:
        return jsonify({
            "error": "Agent not initialized",
            "status": "error"
        }), 503
    
    try:
        data = request.json
        questions = data.get("questions", [])
        
        if not questions:
            return jsonify({
                "error": "Missing 'questions' field in request",
                "status": "error"
            }), 400
        
        # Process batch
        batch_result = cs_agent.handle_batch_inquiries(questions)
        
        return jsonify({
            "status": "success",
            "batch_result": batch_result,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# ============================================================================
# DEMO ENDPOINT (For Google Team)
# ============================================================================

@app.route('/demo', methods=['GET'])
def demo():
    """
    Interactive demo page for testing
    Returns HTML form to test the agent
    """
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CloudPulse Customer Service Agent - Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #4285F4; margin: 0; }
            .header p { color: #666; margin: 5px 0; }
            textarea { font-size: 14px; }
            input, textarea, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { background: #4285F4; color: white; cursor: pointer; border: none; font-weight: bold; }
            button:hover { background: #1a73e8; }
            .response { background: #f9f9f9; padding: 15px; border-left: 4px solid #4285F4; margin-top: 20px; border-radius: 4px; }
            .response h3 { margin-top: 0; }
            .metrics { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
            .badge { padding: 8px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .good { background: #d4edda; color: #155724; }
            .warning { background: #fff3cd; color: #856404; }
            .loading { display: none; text-align: center; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 CloudPulse AI Agent</h1>
                <p>Powered by Gemini | Monitored by Agent Health Monitor</p>
            </div>
            
            <textarea id="question" placeholder="Ask anything about CloudPulse email platform..." rows="3"></textarea>
            <button onclick="askAgent()">Ask Agent</button>
            
            <div class="loading" id="loading">⏳ Processing your question...</div>
            
            <div id="response" style="display:none;">
                <div class="response">
                    <h3>📧 Agent Response:</h3>
                    <p id="agent-response"></p>
                    
                    <h4>📊 Quality Metrics:</h4>
                    <div class="metrics" id="metrics"></div>
                </div>
            </div>
        </div>
        
        <script>
            async function askAgent() {
                const question = document.getElementById('question').value;
                if (!question) {
                    alert('Please enter a question');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('response').style.display = 'none';
                
                try {
                    const response = await fetch('/agent/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({question})
                    });
                    
                    const data = await response.json();
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        document.getElementById('agent-response').textContent = data.response;
                        
                        const metricsHtml = `
                            <span class="badge ${data.quality_score >= 8 ? 'good' : 'warning'}">
                                ⭐ Quality: ${data.quality_score}/10
                            </span>
                            <span class="badge ${!data.hallucination_detected ? 'good' : 'warning'}">
                                🎯 Hallucination: ${data.hallucination_detected ? 'Detected' : 'None'}
                            </span>
                            <span class="badge">⏱️ Latency: ${data.latency_ms.toFixed(0)}ms</span>
                            <span class="badge">💰 Cost: $${data.cost_usd.toFixed(6)}</span>
                            <span class="badge ${data.faq_matched ? 'good' : 'warning'}">
                                📚 FAQ: ${data.faq_matched ? 'Found' : 'Not Found'}
                            </span>
                            <br/>
                            <small style="color: #999;">Trace ID: ${data.trace_id}</small>
                        `;
                        document.getElementById('metrics').innerHTML = metricsHtml;
                        document.getElementById('response').style.display = 'block';
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Request failed: ' + error);
                }
            }
            
            // Allow Enter key to submit
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && e.ctrlKey) askAgent();
            });
        </script>
    </body>
    </html>
    """
    
    return html, 200, {'Content-Type': 'text/html'}

# ============================================================================
# SAMPLE ENDPOINTS (for testing)
# ============================================================================

@app.route('/sample-questions', methods=['GET'])
def sample_questions():
    """Get sample questions for testing"""
    
    samples = [
        "How much does CloudPulse cost?",
        "Is there a free trial?",
        "Can I integrate CloudPulse with Salesforce?",
        "Is CloudPulse GDPR compliant?",
        "How do I schedule emails?",
        "Does CloudPulse track email opens?",
        "Can I use CloudPulse for newsletters?",
        "How do I contact support?",
        "Do you offer annual billing discounts?",
        "What payment methods do you accept?"
    ]
    
    return jsonify({
        "questions": samples,
        "count": len(samples),
        "usage": "POST /agent/batch-test with {\"questions\": [...]}"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)