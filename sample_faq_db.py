# sample_faq_db.py
"""
FAQ Database for CloudPulse - AI Email Platform
Used by Customer Service Agent to answer user questions
"""

FAQ_DATABASE = {
    "pricing": [
        {
            "question": "How much does CloudPulse cost?",
            "answer": "CloudPulse offers flexible pricing: Free Plan ($0/month, up to 1K emails), Starter ($29/month, 50K emails), Professional ($99/month, 500K emails), and Enterprise (custom). All plans include AI-powered drafting, analytics, and API access.",
            "keywords": ["cost", "price", "pricing", "free", "plan", "pay"]
        },
        {
            "question": "Is there a free trial?",
            "answer": "Yes! Our Free Plan allows you to send up to 1,000 emails per month at no cost. No credit card required. Upgrade anytime to higher plans for more volume and advanced features.",
            "keywords": ["free", "trial", "free plan"]
        },
        {
            "question": "Do you offer discounts for annual billing?",
            "answer": "Yes, we offer 20% off annual subscriptions. For example, Professional Plan is $99/month or $950/year (instead of $1,188). Enterprise customers get custom pricing.",
            "keywords": ["discount", "annual", "yearly", "billing"]
        }
    ],
    
    "features": [
        {
            "question": "What is AI email drafting?",
            "answer": "CloudPulse uses Gemini AI to help you write professional emails. Start with a topic or bullet points, and our AI generates complete email drafts you can customize. Saves 70% of writing time.",
            "keywords": ["AI", "draft", "write", "compose", "ai email"]
        },
        {
            "question": "Can I schedule emails?",
            "answer": "Yes! Schedule emails for future delivery. Our smart send-time optimization suggests the best time to send based on recipient timezone and engagement patterns.",
            "keywords": ["schedule", "send time", "optimal", "timezone"]
        },
        {
            "question": "Does CloudPulse track email opens and clicks?",
            "answer": "Absolutely. CloudPulse provides detailed analytics including open rates, click rates, bounce rates, and recipient engagement timelines. Real-time dashboards show campaign performance.",
            "keywords": ["analytics", "track", "open", "click", "metrics"]
        },
        {
            "question": "Can I use CloudPulse for newsletters?",
            "answer": "Yes! CloudPulse is perfect for newsletters. Features include list segmentation, A/B testing, beautiful templates, and GDPR-compliant unsubscribe options. Thousands of creators use CloudPulse for newsletters.",
            "keywords": ["newsletter", "broadcast", "list", "template"]
        }
    ],
    
    "integration": [
        {
            "question": "How do I integrate CloudPulse with my app?",
            "answer": "CloudPulse provides REST APIs and SDKs for Python, Node.js, Go, and Java. Full documentation at api.cloudpulse.io. Basic setup takes 15 minutes.",
            "keywords": ["API", "integrate", "connect", "SDK", "integration"]
        },
        {
            "question": "Does CloudPulse work with Zapier?",
            "answer": "Yes! CloudPulse is available on Zapier with 100+ pre-built integrations. Connect to Salesforce, Stripe, HubSpot, and more with no code.",
            "keywords": ["Zapier", "workflow", "automation", "no-code"]
        },
        {
            "question": "Can I sync my contacts from Gmail?",
            "answer": "Yes. CloudPulse supports bulk import from Gmail, Outlook, CSV files, and via API. You can also enable one-way sync to keep lists updated automatically.",
            "keywords": ["sync", "import", "contacts", "Gmail", "contacts list"]
        }
    ],
    
    "security": [
        {
            "question": "Is CloudPulse secure?",
            "answer": "CloudPulse uses enterprise-grade security: TLS encryption, SOC 2 Type II certified, GDPR compliant, and zero-knowledge architecture. Your email content never touches our servers unencrypted.",
            "keywords": ["secure", "security", "encrypted", "GDPR", "compliance"]
        },
        {
            "question": "Can CloudPulse see my email content?",
            "answer": "No. We use end-to-end encryption. Your emails are encrypted at rest and in transit. Our AI features work on anonymized metadata only.",
            "keywords": ["privacy", "encryption", "content", "confidential"]
        },
        {
            "question": "Is CloudPulse GDPR compliant?",
            "answer": "Yes. CloudPulse is fully GDPR compliant. We process personal data only with valid legal basis, provide data export/deletion on request, and maintain Data Processing Agreements (DPA) with all customers.",
            "keywords": ["GDPR", "privacy", "compliance", "legal"]
        }
    ],
    
    "support": [
        {
            "question": "How do I contact support?",
            "answer": "Email support@cloudpulse.io or use the live chat in your dashboard (available 24/7). Enterprise customers have dedicated account managers. Average response time is under 2 hours.",
            "keywords": ["support", "help", "contact", "chat", "email support"]
        },
        {
            "question": "What if my email bounces?",
            "answer": "CloudPulse automatically identifies bounced emails and removes them from your list. We categorize bounces (hard bounce, soft bounce, spam complaint) so you can improve list quality.",
            "keywords": ["bounce", "failed", "delivery", "undeliverable"]
        },
        {
            "question": "How do I reduce spam complaints?",
            "answer": "Best practices: 1) Use clear From address, 2) Include physical mailing address, 3) Provide easy unsubscribe, 4) Send relevant content, 5) Use CloudPulse's list segmentation. Monitor your spam complaint rate in Analytics.",
            "keywords": ["spam", "complaint", "reputation", "unsubscribe"]
        }
    ],
    
    "billing": [
        {
            "question": "When do I get charged?",
            "answer": "Monthly plans charge on the same day each month. Annual plans charge once per year. You can cancel anytime. Free Plan has no charges.",
            "keywords": ["charged", "billing", "payment", "charge date"]
        },
        {
            "question": "Can I upgrade or downgrade anytime?",
            "answer": "Yes! Change your plan anytime. Upgrade immediately, or downgrade at the end of your billing cycle. Pro-rata refunds apply for downgrades mid-month.",
            "keywords": ["upgrade", "downgrade", "change plan"]
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "CloudPulse accepts all major credit cards (Visa, Mastercard, American Express, Discover), PayPal, and wire transfer for annual Enterprise plans.",
            "keywords": ["payment", "credit card", "PayPal", "method"]
        }
    ]
}

def search_faq(user_query):
    """
    Search FAQ database for relevant answers
    Returns list of (question, answer, relevance_score) tuples
    """
    user_query_lower = user_query.lower()
    results = []
    
    for category, faqs in FAQ_DATABASE.items():
        for faq in faqs:
            question = faq["question"].lower()
            keywords = faq["keywords"]
            answer = faq["answer"]
            
            # Calculate relevance score
            relevance = 0
            
            # Keyword matching
            for keyword in keywords:
                if keyword in user_query_lower:
                    relevance += 1
            
            # Question substring matching
            if any(word in user_query_lower.split() for word in question.split()):
                relevance += 0.5
            
            if relevance > 0:
                results.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": category,
                    "relevance": relevance
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:3]  # Return top 3 matches

def get_all_faq_topics():
    """Get all FAQ topics for agent awareness"""
    topics = []
    for category, faqs in FAQ_DATABASE.items():
        for faq in faqs:
            topics.append(faq["question"])
    return topics

if __name__ == "__main__":
    # Test the FAQ database
    test_queries = [
        "How much does it cost?",
        "Is there a free trial?",
        "How do I integrate with my app?",
        "Is it secure?",
        "How do I contact support?"
    ]
    
    for query in test_queries:
        print(f"\n📧 Query: {query}")
        results = search_faq(query)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['question']} (relevance: {result['relevance']})")
            print(f"     Answer: {result['answer'][:100]}...")