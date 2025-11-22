import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

print("🚀 Starting Inventory Agent (Mock)...")

def check_stock_level(product_name: str) -> str:
    """Check current stock levels for a product from database"""
    product_response = supabase.table('products')\
        .select('*')\
        .ilike('name', f'%{product_name}%')\
        .execute()
    
    if not product_response.data:
        return f"❌ Product '{product_name}' not found in catalog."
    
    product = product_response.data[0]

    inventory_response = supabase.table('inventory')\
        .select('*')\
        .eq('product_id', product['id'])\
        .execute()
    
    if inventory_response.data:
        inventory = inventory_response.data[0]
        available_stock = inventory['stock_quantity']

        if available_stock == 0:
            status_emoji = "❌"
            status_msg = "Out of Stock"
        elif available_stock <= 5:
            status_emoji = "⚠️"
            status_msg = "Low Stock"
        else:
            status_emoji = "✅"
            status_msg = "In Stock"

        return f"""
    {status_emoji} **{product['name']} - Stock Status**
    📦 Current Stock: {available_stock} units
    📊 Status: {status_msg}
    """

    else:
        return f"❌ No inventory data found for {product['name']}"


def check_restock_schedule(product_name: str) -> str:
    """Check inventory status and provide restock info from database"""
    # Find the product
    product_response = supabase.table('products')\
        .select('*')\
        .ilike('name', f'%{product_name}%')\
        .execute()
    
    if not product_response.data:
        return f"❌ Product '{product_name}' not found."
    
    product = product_response.data[0]
    
    # Get inventory
    inventory_response = supabase.table('inventory')\
        .select('*')\
        .eq('product_id', product['id'])\
        .execute()
    
    if inventory_response.data:
        inventory = inventory_response.data[0]
        
        # Simple restock logic based on stock level
        if inventory['stock_quantity'] == 0:
            restock_info = "🔄 Restock scheduled for next week"
        elif inventory['stock_quantity'] <= 5:
            restock_info = "🔄 Restock scheduled in 3-5 days"
        else:
            restock_info = "✅ Sufficient stock, no restock needed"
        
        return f"""
📦 **{product['name']} - Restock Information**
📊 Current Stock: {inventory['stock_quantity']} units
📅 {restock_info}
"""
    else:
        return f"❌ No inventory information available for {product['name']}"

def get_low_stock_items() -> str:
    """Get list of items with low stock from database"""
    inventory_response = supabase.table('inventory')\
        .select('*')\
        .lte('stock_quantity', 5)\
        .execute()
    
    if inventory_response.data:
        low_stock_items = []

        for inventory in inventory_response.data:
            # Get product details for each low stock item
            product_response = supabase.table('products')\
                .select('name')\
                .eq('id', inventory['product_id'])\
                .execute()
            
            if product_response.data:
                product = product_response.data[0]
                status = "Out of Stock" if inventory['stock_quantity'] == 0 else "Low Stock"
                
                low_stock_items.append({
                    'name': product['name'],
                    'current_stock': inventory['stock_quantity'],
                    'status': status
                })
        
        if low_stock_items:
            items_text = "\n".join([
                f"  • {item['name']}: {item['current_stock']} units ({item['status']})"
                for item in low_stock_items
            ])
            return f"⚠️ **Low Stock Alert** ⚠️\n\n{items_text}"
    
    return "✅ All items have sufficient stock levels."

# Create Inventory Agent
inventory_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash-lite", 
        api_key=os.environ.get("GOOGLE_API_KEY")
    ),
    name="inventory_agent",
    description="Manages inventory tracking, stock levels, and restocking schedules using data from a database.",
    instruction="""
    You are an inventory management specialist using demonstration data.
    
    Your capabilities:
    • Check current stock levels and availability status
    • Provide restocking schedules and dates
    • Identify low stock and out-of-stock items
    
    Stock Status Meanings:
    ✅ In Stock: Plenty available
    ⚠️ Low Stock: Below reorder level
    ❌ Out of Stock: No units available
    
    Always provide clear stock status with emojis for better readability.
    """,
    tools=[check_stock_level, check_restock_schedule, get_low_stock_items]
)

print("✅ Inventory Agent created!")

# Create A2A app
app = to_a2a(inventory_agent, port=8002)
agent = inventory_agent



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)


print("🌐 Inventory A2A server ready on port 8002")