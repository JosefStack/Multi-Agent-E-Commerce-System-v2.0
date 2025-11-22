import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types
from datetime import datetime, timedelta

from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get('SUPABASE_KEY')
)

print("🚀 Starting Shipping Agent (Mock)...")


def get_shipping_estimates(zip_code: str, shipping_method: str = "standard") -> str:
    """
    Calculate shipping cost and delivery date
    Example: User asks "Shipping to 94105 with express shipping"
    """
    
    # STEP 1: GET SHIPPING METHOD FROM DATABASE
    shipping_response = supabase.table('shipping_rates')\
        .select('*')\
        .ilike('shipping_method', f'%{shipping_method}%')\
        .execute()
    
    # STEP 2: CHECK IF SHIPPING METHOD EXISTS
    if not shipping_response.data:
        # Get all available shipping methods to show user
        all_methods_response = supabase.table('shipping_rates')\
            .select('shipping_method, carrier, base_cost, base_days')\
            .execute()
        
        if all_methods_response.data:
            methods_list = "\n".join([
                f"  • {method['shipping_method'].title()}: ${method['base_cost']} - {method['base_days']} days via {method['carrier']}"
                for method in all_methods_response.data
            ])
            return f"❌ Shipping method '{shipping_method}' not found.\n\n🚚 Available methods:\n{methods_list}"
        else:
            return f"❌ Shipping method '{shipping_method}' not available."
    
    # STEP 3: GET SHIPPING METHOD DETAILS
    shipping_method_data = shipping_response.data[0]
    
    # STEP 4: CALCULATE DELIVERY DATE
    base_days = shipping_method_data['base_days']
    
    # Add realistic variability based on zip code region
    region_adjustment = 0
    if zip_code:
        region_prefix = zip_code[:3]  # First 3 digits of zip code
        
        # Check if we have regional data for this zip code
        region_response = supabase.table('regional_delivery')\
            .select('delivery_adjustment')\
            .eq('region_prefix', region_prefix)\
            .execute()
        
        if region_response.data:
            region_adjustment = region_response.data[0]['delivery_adjustment']
    
    total_days = base_days + region_adjustment
    delivery_date = datetime.now() + timedelta(days=total_days)
    
    # STEP 5: FORMAT RESPONSE
    return f"""
🚚 **Shipping to {zip_code}**
📦 Method: {shipping_method_data['shipping_method'].title()} ({shipping_method_data['carrier']})
💰 Cost: ${shipping_method_data['base_cost']}
⏱️ Delivery Time: {total_days} business day{'s' if total_days != 1 else ''}
📅 Expected Delivery: {delivery_date.strftime('%A, %B %d, %Y')}
📝 {shipping_method_data['description']}
"""


def track_package(tracking_number: str) -> str:
    """
    Track a package using tracking number
    Example: User asks "Track package TRK123456789"
    """
    
    # STEP 1: SEARCH FOR PACKAGE IN DATABASE
    tracking_response = supabase.table('package_tracking')\
        .select('*')\
        .ilike('tracking_number', f'%{tracking_number}%')\
        .execute()
    
    # STEP 2: CHECK IF PACKAGE FOUND
    if tracking_response.data:
        package = tracking_response.data[0]
        
        # STEP 3: DETERMINE STATUS EMOJI AND DESCRIPTION
        status_emojis = {
            "processing": "📦",
            "in_transit": "🚚", 
            "out_for_delivery": "📮",
            "delivered": "✅"
        }
        
        status_descriptions = {
            "processing": "Your package is being prepared for shipment",
            "in_transit": "Your package is on the way to its destination",
            "out_for_delivery": "Your package is out for delivery today",
            "delivered": "Your package has been successfully delivered"
        }
        
        emoji = status_emojis.get(package['status'], '📦')
        description = status_descriptions.get(package['status'], '')
        
        # STEP 4: FORMAT TRACKING INFORMATION
        return f"""
{emoji} **Package Tracking: {package['tracking_number'].upper()}**
📊 Status: {package['status'].replace('_', ' ').title()}
{description}
📍 Current Location: {package['current_location']}
📅 Estimated Delivery: {package['estimated_delivery']}
🚚 Carrier: {package['carrier']}
"""
    else:
        # STEP 5: PACKAGE NOT FOUND
        return f"❌ Tracking number '{tracking_number}' not found.\n\n💡 Please verify your tracking number or contact support."


def get_shipping_options() -> str:
    """
    Show all available shipping methods
    Example: User asks "What shipping options do you have?"
    """
    
    # STEP 1: GET ALL SHIPPING RATES FROM DATABASE
    shipping_response = supabase.table('shipping_rates')\
        .select('*')\
        .execute()
    
    # STEP 2: FORMAT EACH SHIPPING OPTION
    options = []
    for method in shipping_response.data:
        day_text = "day" if method['base_days'] == 1 else "days"
        options.append(
            f"  • **{method['shipping_method'].title()}**: ${method['base_cost']} - {method['base_days']} {day_text} via {method['carrier']}\n    {method['description']}"
        )
    
    # STEP 3: COMBINE ALL OPTIONS
    return "🚚 **Available Shipping Options**\n\n" + "\n\n".join(options)


def calculate_free_shipping_eligibility(order_total: float) -> str:
    """
    Check if order qualifies for free shipping
    Example: User asks "Do I get free shipping on $50 order?"
    """
    
    # STEP 1: GET FREE SHIPPING METHOD
    free_shipping_response = supabase.table('shipping_rates')\
        .select('*')\
        .ilike('shipping_method', '%free%')\
        .execute()
    
    if free_shipping_response.data:
        free_shipping_method = free_shipping_response.data[0]
        
        # STEP 2: CHECK ELIGIBILITY (assuming $35 minimum for free shipping)
        free_shipping_minimum = 35.00
        
        if order_total >= free_shipping_minimum:
            return f"🎉 Congratulations! Your order of ${order_total:.2f} qualifies for FREE shipping! ({free_shipping_method['description']})"
        else:
            needed = free_shipping_minimum - order_total
            return f"📦 Add ${needed:.2f} more to your order to qualify for FREE shipping!"
    else:
        return "📦 Free shipping is not currently available."


# Create Shipping Agent
shipping_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash-lite",
        api_key=os.environ.get("GOOGLE_API_KEY")
    ),
    name="shipping_agent", 
    description="Provides shipping estimates, delivery tracking, and shipping options using data from database.",
    instruction="""
    You are a shipping and delivery specialist using demonstration data.
    
    Your capabilities:
    • Provide shipping cost estimates and delivery dates
    • Track packages using tracking numbers
    • Explain available shipping options and carriers
    • Check free shipping eligibility
    
    Shipping Methods Available:
    • Standard (5 days, $4.99)
    • Expedited (2 days, $12.99) 
    • Overnight (1 day, $24.99)
    • Free (7 days, $0.00) - Orders over $35
    
    Sample Tracking Numbers: TRK123456789, TRK987654321, TRK456789123
    
    Always provide clear delivery estimates and tracking information.
    Use emojis to make the information more engaging.
    """,
    tools=[get_shipping_estimates, track_package, get_shipping_options, calculate_free_shipping_eligibility]
)

print("✅ Shipping Agent created!")

# Create A2A app
app = to_a2a(shipping_agent, port=8003)
agent = shipping_agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)



print("🌐 Shipping A2A server ready on port 8003")