import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

import json
from supabase import create_client, Client

load_dotenv()


# Initialize Supabase client
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

print("🚀 Starting Product Catalog Agent (Real Database)...")

def get_product_details(product_name: str) -> str:
    """Get detailed product information from database"""
    response = supabase.table('products')\
            .select('*')\
            .ilike('name', f'%{product_name}%')\
            .execute()
    
    if response.data:
        product = response.data[0]

        features = "\n".join(f" • {feature}" for feature in product.get('features', []))

        specs = product.get('specifications', {})
        spec_text = "\n".join([f" • {key}: {value}" for key, value in specs.items()])

        return f"""
📱 **{product['name']}** - ${product['price']}
🏷️  Brand: {product['brand']}
📂 Category: {product['category']}

📝 Description: {product['description']}

⚙️ Specifications:
{spec_text}

✨ Features:
{features}

💡 Need stock information? Ask our inventory agent!
"""

    else:
        similar_response = supabase.table('products')\
        .select('name', 'price')\
        .execute()

        if similar_response.data:
            suggestions = "\n".join([f"  • {p['name']} - ${p['price']}" for p in similar_response.data[:3]])
            return f"❌ Product '{product_name}' not found.\n\n🔍 Similar products:\n{suggestions}"
        else:
            return f"❌ Product '{product_name}' not found in our catalog."


def search_products_tool(query: str, category: str = "") -> str:
    """Search products in in database by name, description, or category"""
    response = supabase.table('products')\
        .select('*')\
        .or_(f"name.ilike.%{query}%,description.ilike.%{query}%,category.ilike.%{query}%")\
        .execute()
    
    if response.data:
        product_list = "\n".join([
            f"  • {p['name']} (${p['price']}) - {p['description'][:80]}..." 
            for p in response.data[:5]  # Show first 5 results
        ])
        return f"🔍 Found {len(response.data)} products:\n{product_list}"
    else:
        return f"❌ No products found for '{query}'."


def list_categories() -> str:
    """List all available product categories from the database"""
    response = supabase.table('products')\
        .select('category')\
        .execute()
    
    categories = list(set([p['category'] for p in response.data]))

    return "🛍️ Available Categories:\n" + "\n".join([f"  • {cat}" for cat in categories])


    
# Create Product Catalog Agent
product_catalog_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash-lite",
        api_key=os.environ.get("GOOGLE_API_KEY")
    ),
    name="product_catalog_agent",
    description="Provides detailed product information, specifications, and search capabilities using a real database.",
    instruction="""
    You are a friendly product catalog specialist using mock demonstration data.
    
    Your capabilities:
    • Get detailed product information with specs and features
    • Search for products by name or category  
    • List available product categories
    
    You use REAL DATA from the database.

    Always be helpful and suggest similar products if exact match not found.
    Mention that this is demo data for testing purposes.
    """,
    tools=[get_product_details, search_products_tool, list_categories]
)

print("✅ Product Catalog Agent created with real database!")

# Create A2A app
app = to_a2a(product_catalog_agent, port=8001)
agent = product_catalog_agent


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


print("🌐 Product Catalog A2A server ready on port 8001")