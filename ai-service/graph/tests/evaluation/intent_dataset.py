
INTENT_DATASET = [
    {
        "query": "Where is my order 123?",
        "expected_intent": "ORDER_STATUS",
    },
    {
        "query": "Has my package been shipped?",
        "expected_intent": "ORDER_STATUS",
    },
    {
        "query": "What is your refund policy?",
        "expected_intent": "REFUND_POLICY",
    },
    {
        "query": "Can I return a damaged item?",
        "expected_intent": "REFUND_POLICY",
    },
    {
        "query": "Show me smartphones under 20000",
        "expected_intent": "PRODUCT_SEARCH",
    },
    {
        "query": "Do you have this laptop in stock?",
        "expected_intent": "PRODUCT_SEARCH",
    },
    {
        "query": "Please cancel order 123",
        "expected_intent": "ORDER_CANCEL",
    },
    {
        "query": "I don't want my order anymore",
        "expected_intent": "ORDER_CANCEL",
    },
]
