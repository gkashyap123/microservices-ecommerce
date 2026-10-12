
from llm.client import get_llm
from graph.state import AgentState


def extract_product_list(products):
    """Support the Product Service's paginated response format."""
    if isinstance(products, dict):
        results = products.get("results", [])
        return results if isinstance(results, list) else []

    if isinstance(products, list):
        return products

    return []


async def product_response_node(state: AgentState) -> AgentState:
    products_data = state.get("products")
    product_list = extract_product_list(products_data)

    if not product_list:
        return {
            **state,
            "response": (
                "I couldn't find any products matching your request."
            ),
        }

    message = state["user_message"].lower()

    # Calculate stock ranking from actual product data.
    if any(
        phrase in message
        for phrase in (
            "highest stock",
            "most stock",
            "maximum stock",
            "highest inventory",
            "most inventory",
        )
    ):
        valid_products = [
            product
            for product in product_list
            if isinstance(product, dict)
            and isinstance(product.get("stock"), (int, float))
        ]

        if not valid_products:
            return {
                **state,
                "response": (
                    "I found products, but their stock quantities "
                    "are unavailable for comparison."
                ),
            }

        highest_stock = max(
            product["stock"] for product in valid_products
        )

        winners = [
            product
            for product in valid_products
            if product["stock"] == highest_stock
        ]

        winner_details = "\n".join(
            f'- {product.get("name", "Unknown product")}: '
            f'{product["stock"]} units in stock; '
            f'price {product.get("price", "unavailable")}'
            for product in winners
        )

        return {
            **state,
            "response": (
                "Among the products retrieved, the highest-stock "
                f"product(s) are:\n{winner_details}"
            ),
        }

    # Normal product search response.
    llm = get_llm()

    prompt = f"""
You are an e-commerce shopping assistant.

Customer request:
{state["user_message"]}

Products retrieved from the Product Service:
{product_list}

Rules:
1. Recommend only products in the supplied data.
2. Never invent product names, prices, stock, or specifications.
3. Preserve the customer's requested product category and budget.
4. If a field is missing, say it is unavailable.
5. Keep the response concise.
"""

    result = await llm.ainvoke(prompt)

    return {
        **state,
        "response": result.content,
    }
