import asyncio
import subprocess
import sys
import time

def start_all_agents():
    """Start all agents and wait for them to be ready"""
    agents = [
        "agents/product_catalog_agent/agent.py",
        "agents/inventory_agent/agent.py", 
        "agents/shipping_agent/agent.py"
    ]
    
    for agent in agents:
        subprocess.Popen([sys.executable, agent])
        time.sleep(2)
    
    time.sleep(5)  # Wait for all agents to start
    print("✅ All agents started!")

async def chat_with_agent():
    """Chat with the customer support agent"""
    sys.path.append('agents/customer_support_agent')
    from agents.customer_support_agent.agent import runner, run_session
    
    print("💬 Customer Support is ready! Ask me anything about products, stock, or shipping!")
    
    session_id = 1
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ['quit', 'exit']:
            break
        await run_session(runner, question, f"chat_{session_id}")
        session_id += 1

if __name__ == "__main__":
    start_all_agents()
    # asyncio.run(chat_with_agent())