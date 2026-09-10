# customer_service_agent.py
"""
Customer Service Agent for CloudPulse
Built with Google Agent Development Kit (ADK)
Answers FAQ questions and logs all interactions for monitoring/evaluation
"""

import time
import os
from datetime import datetime
from agent_tools import (
    lookup_faq,
    generate_response_with_gemini,
    assess_response_quality,
    log_agent_trace
)
from dotenv import load_dotenv
load_dotenv()

class CustomerServiceAgent:
    """
    CloudPulse Customer Service Agent
    Handles customer inquiries using FAQ + Gemini
    """
    
    def __init__(self, agent_id="cs-agent-v1"):
        self.agent_id = agent_id
        self.agent_type = "customer_service"
        self.model = "gemini-3.5-flash"
        self.interaction_count = 0
        
        # Verify Gemini API key is set
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("❌ GEMINI_API_KEY environment variable not set. Add to .env file!")
        
        print(f"✅ Agent initialized: {self.agent_id}")
    
    def process_customer_inquiry(self, user_input: str) -> dict:
        """
        Main agent function: Process a customer question end-to-end
        
        1. Search FAQ database
        2. Generate response with Gemini
        3. Assess response quality
        4. Log interaction trace
        5. Return response to customer
        
        Args:
            user_input: Customer's question
        
        Returns:
            dict with response and metadata
        """
        
        self.interaction_count += 1
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"📧 Interaction #{self.interaction_count}")
        print(f"{'='*60}")
        print(f"👤 Customer: {user_input}")
        
        # Step 1: Search FAQ database
        print(f"\n[Step 1] Searching FAQ database...")
        faq_results = lookup_faq(user_input)
        
        if faq_results["status"] == "found":
            print(f"   ✅ Found {len(faq_results['results'])} matching FAQs")
            for i, result in enumerate(faq_results["results"], 1):
                print(f"      {i}. {result['question']} (relevance: {result['relevance']})")
        else:
            print(f"   ⚠️  No direct FAQ match - will use general knowledge")
        
        # Step 2: Generate response with Gemini
        print(f"\n[Step 2] Generating response with Gemini...")
        try:
            response_result = generate_response_with_gemini(
                user_input,
                faq_results,
                self.model
            )
            agent_response = response_result["response"]
            response_tokens = response_result["response_tokens"]
            input_tokens = response_result["input_tokens"]
            success = True
            error_message = None
            
            print(f"   ✅ Response generated")
            print(f"      Tokens used: {input_tokens} input, {response_tokens} output")
        
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            agent_response = "I apologize, but I'm having trouble generating a response. Please contact our support team at support@cloudpulse.io"
            response_tokens = len(agent_response.split())
            input_tokens = len(user_input.split())
            success = False
            error_message = str(e)
        
        # Step 3: Assess response quality
        print(f"\n[Step 3] Assessing response quality...")
        quality_assessment = assess_response_quality(
            user_input,
            faq_results,
            agent_response
        )
        
        quality_score = quality_assessment["quality_score"]
        hallucination_detected = quality_assessment["hallucination_detected"]
        
        print(f"   Quality Score: {quality_score}/10")
        print(f"   Hallucination Detected: {hallucination_detected}")
        if quality_assessment["issues"]:
            for issue in quality_assessment["issues"]:
                print(f"      ⚠️  {issue}")
        
        # Step 4: Log interaction to BigQuery
        print(f"\n[Step 4] Logging trace to BigQuery...")
        latency_ms = (time.time() - start_time) * 1000
        
        trace_result = log_agent_trace(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            user_input=user_input,
            agent_response=agent_response,
            response_tokens=response_tokens,
            input_tokens=input_tokens,
            latency_ms=latency_ms,
            success=success,
            decision_quality_score=quality_score,
            hallucination_detected=hallucination_detected,
            error_message=error_message
        )
        
        if trace_result["status"] == "success":
            print(f"   ✅ Trace logged: {trace_result['trace_id']}")
            print(f"      Cost: ${trace_result['cost_usd']:.6f}")
        else:
            print(f"   ❌ Trace logging failed: {trace_result.get('error', 'Unknown')}")
        
        # Step 5: Return complete response
        print(f"\n[Response]")
        print(f"🤖 Agent: {agent_response}")
        print(f"{'='*60}\n")
        
        return {
            "success": success,
            "agent_response": agent_response,
            "quality_score": quality_score,
            "hallucination_detected": hallucination_detected,
            "faq_matched": faq_results["status"] == "found",
            "latency_ms": round(latency_ms, 2),
            "cost_usd": trace_result.get("cost_usd", 0),
            "trace_id": trace_result.get("trace_id", None),
            "metadata": {
                "faq_results_count": len(faq_results.get("results", [])),
                "quality_issues": quality_assessment["issues"],
                "input_tokens": input_tokens,
                "output_tokens": response_tokens,
            }
        }
    
    def handle_batch_inquiries(self, inquiries: list) -> dict:
        """
        Process multiple customer inquiries
        
        Args:
            inquiries: List of customer questions
        
        Returns:
            dict with aggregated results
        """
        
        print(f"\n🚀 Processing {len(inquiries)} inquiries...\n")
        
        results = []
        total_latency = 0
        total_cost = 0
        quality_scores = []
        hallucination_count = 0
        
        for i, inquiry in enumerate(inquiries, 1):
            print(f"Processing inquiry {i}/{len(inquiries)}...")
            result = self.process_customer_inquiry(inquiry)
            results.append(result)
            
            total_latency += result["latency_ms"]
            total_cost += result["cost_usd"]
            quality_scores.append(result["quality_score"])
            if result["hallucination_detected"]:
                hallucination_count += 1
        
        # Calculate aggregates
        avg_latency = total_latency / len(inquiries)
        avg_quality = sum(quality_scores) / len(quality_scores)
        success_rate = sum(1 for r in results if r["success"]) / len(inquiries)
        
        return {
            "total_inquiries": len(inquiries),
            "successful": sum(1 for r in results if r["success"]),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_quality_score": round(avg_quality, 2),
            "success_rate": round(success_rate * 100, 2),
            "total_cost_usd": round(total_cost, 4),
            "hallucination_count": hallucination_count,
            "hallucination_rate": round(hallucination_count / len(inquiries) * 100, 2),
            "results": results
        }
    
    def get_stats(self) -> dict:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "total_interactions": self.interaction_count,
            "model": self.model,
            "status": "active"
        }


# Sample inquiries for testing
SAMPLE_INQUIRIES = [
    "How much does CloudPulse cost?",
    "Is there a free trial?",
    "Can I integrate CloudPulse with my Salesforce?",
    "Is CloudPulse secure and GDPR compliant?",
    "How do I schedule emails for later?",
    "Does CloudPulse track email opens?",
    "Can I use CloudPulse for newsletters?",
    "How do I contact your support team?",
    "Do you offer discounts for annual billing?",
    "What payment methods do you accept?",
]


def main():
    """Main entry point - demo the agent"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  CloudPulse Customer Service Agent - Powered by Gemini         ║
    ║  Agent ID: cs-agent-v1                                         ║
    ║  Type: Conversational AI + FAQ Retrieval                       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    
    """)

    
    
    

    
    # Initialize agent
    agent = CustomerServiceAgent()
    
    # Demo options
    print("\n🎯 Demo Options:")
    print("  1. Single inquiry (interactive)")
    print("  2. Batch test (10 pre-defined questions)")
    print("  3. Custom inquiry")
    
    choice = input("\nSelect option (1-3, or press Enter for batch): ").strip() or "2"
    
    if choice == "1":
        # Interactive mode
        user_input = input("\n👤 Enter your question about CloudPulse: ").strip()
        if user_input:
            result = agent.process_customer_inquiry(user_input)
    
    elif choice == "2":
        # Batch test
        print("\n📊 Running batch test with 10 sample inquiries...\n")
        batch_result = agent.handle_batch_inquiries(SAMPLE_INQUIRIES)
        
        print("\n" + "="*60)
        print("📊 BATCH TEST RESULTS")
        print("="*60)
        print(f"Total Inquiries: {batch_result['total_inquiries']}")
        print(f"Successful: {batch_result['successful']}")
        print(f"Success Rate: {batch_result['success_rate']}%")
        print(f"\nAvg Latency: {batch_result['avg_latency_ms']}ms")
        print(f"Avg Quality Score: {batch_result['avg_quality_score']}/10")
        print(f"Total Cost: ${batch_result['total_cost_usd']}")
        print(f"Hallucination Rate: {batch_result['hallucination_rate']}%")
        print("="*60)
    
    elif choice == "3":
        # Custom inquiry
        user_input = input("\n👤 Enter your question: ").strip()
        if user_input:
            result = agent.process_customer_inquiry(user_input)
    
    else:
        print("Invalid option. Running batch test...")
        batch_result = agent.handle_batch_inquiries(SAMPLE_INQUIRIES)
    
    # Show agent status
    print("\n✅ Agent Statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()