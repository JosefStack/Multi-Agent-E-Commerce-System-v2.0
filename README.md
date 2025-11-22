# 🤖 Multi-Agent E-commerce System v2.0

**Implements Multi-Agents | Sessions | Memory | A2A Protocol | Real PostgreSQL Database**

A production-ready multi-agent AI system with persistent memory and real database integration. Specialized AI agents collaborate seamlessly using the A2A protocol with conversation memory and real data.

**What's new in v 2.0?**
- 🗄️ **Real PostgreSQL Database** (Supabase) - No more mock data!
- 🧠 **Persistent Session Memory** - Remembers conversations across sessions
- 📊 **36+ Real Products** - Comprehensive product catalog
- 🔄 **Automated Memory Management** - Automatic save/recall of conversations
- 🎯 **Production Architecture** - Error handling, retry logic, scalable design

🎯 What Makes This Special
This isn't just another chatbot - it's a scalable microservices architecture where specialized AI agents work together via A2A protocol.


** **
**🏗️ System Architecture**

<img width="2000" height="700" alt="system_architecuture" src="https://github.com/user-attachments/assets/2f196f41-60cb-4178-90fd-d9a3931e45bc" />



** **
**🤖 Agent Specializations**


| Agent	Role	      | Capabilities                                                                   |
|-------------------|--------------------------------------------------------------------------------|
| Customer Support  |	Master Coordinator	Session memory, agent coordination, conversation flow      |
| Product Catalog  	| Product Specialist	Product details, specifications, search & recommendations  |
| Inventory       	| Stock Manager	Stock levels, restocking schedules, low stock alerts             |  
| Shipping        	| Delivery Expert	Shipping estimates, package tracking, carrier options          |

** ** 

**🚀 Quick Start**

Prerequisites:                                                                                                                                                                                             
+ Python 3.11+                                                                                                                                                                                                
+ google-adk                                                                                                                                                                                             
+ Google AI Studio API key
+ Supabase account (free tier)
                                                                                                                                                                                                  
**Installation**

1. Clone repository
```bash
                                                                                                                                                                                      
git clone https://github.com/yourusername/multi-agent-commerce-system-v1
cd multi-agent-commerce-system-v1
```                                                   

2. Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate.bat  # Windows

3. Install dependencies
pip install -r requirements.txt

4. Setup environment variables
Add your GOOGLE_API_KEY to .env file

5. Run
python start_system.py

** **
**Project Structure**

<img width="328" height="566" alt="image" src="https://github.com/user-attachments/assets/9cead2a0-7fb2-49cc-959b-6caff4d5b251" />


** **
**Database Setup**
1. Create Supabase Project
+ Go to supabase.come
+ Create free account and new project
+ Get your project URL and anon public key

2. Create Database Tables
Run this SQL in Supabase SQL Editor
```
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Products table
CREATE TABLE products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    specifications JSONB,
    features TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inventory table
CREATE TABLE inventory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    stock_quantity INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_stock',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Shipping rates table
CREATE TABLE shipping_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    shipping_method VARCHAR(50) NOT NULL,
    carrier VARCHAR(50) NOT NULL,
    base_cost DECIMAL(6,2) NOT NULL,
    base_days INTEGER NOT NULL,
    description TEXT
);

-- Package tracking table
CREATE TABLE package_tracking (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tracking_number VARCHAR(100) UNIQUE,
    carrier VARCHAR(50),
    status VARCHAR(50) DEFAULT 'processing',
    current_location VARCHAR(255),
    estimated_delivery DATE
);
```

3. Add Sample Data
Run this SQL in Supabase SQL Editor to add sample products and data
```
-- Sample Products
INSERT INTO products (name, description, price, category, brand, specifications, features) VALUES
('iPhone 15 Pro', 'Latest iPhone with A17 Pro chip', 999.99, 'Electronics', 'Apple', 
 '{"storage": "128GB", "color": "Natural Titanium", "screen": "6.1-inch"}'::jsonb,
 '{"Face ID", "5G", "Pro Camera System"}'),
 
('Samsung Galaxy S24', 'Advanced Android smartphone', 799.99, 'Electronics', 'Samsung',
 '{"storage": "256GB", "color": "Onyx Black", "screen": "6.2-inch"}'::jsonb,
 '{"5G", "Advanced Camera", "Fast Charging"}'),
 
('MacBook Pro 14"', 'Powerful laptop for professionals', 1999.99, 'Computers', 'Apple',
 '{"chip": "M3 Pro", "memory": "18GB", "storage": "512GB"}'::jsonb,
 '{"Retina Display", "Touch Bar", "Long Battery Life"}'),

('Sony WH-1000XM5', 'Industry-leading noise cancelling headphones', 399.99, 'Audio', 'Sony',
 '{"type": "Over-ear", "battery": "30 hours", "connectivity": "Bluetooth 5.2"}'::jsonb,
 '{"Noise Cancelling", "Touch Controls", "Quick Charge"}'),

('iPad Air', 'Powerful tablet for work and creativity', 599.99, 'Tablets', 'Apple',
 '{"screen": "10.9-inch", "storage": "64GB", "chip": "M1"}'::jsonb,
 '{"M1 Chip", "Apple Pencil Support", "All-day Battery"}');

-- Sample Inventory
INSERT INTO inventory (product_id, stock_quantity, status) 
SELECT id, 
       CASE 
         WHEN name LIKE '%iPhone%' THEN 45
         WHEN name LIKE '%Samsung%' THEN 25
         WHEN name LIKE '%MacBook%' THEN 8
         WHEN name LIKE '%Sony%' THEN 22
         WHEN name LIKE '%iPad%' THEN 30
         ELSE 15
       END,
       CASE 
         WHEN name LIKE '%MacBook%' THEN 'low_stock'
         ELSE 'in_stock'
       END
FROM products;

-- Sample Shipping Rates
INSERT INTO shipping_rates (shipping_method, carrier, base_cost, base_days, description) VALUES
('standard', 'USPS', 4.99, 5, 'Economy shipping with tracking'),
('express', 'FedEx', 12.99, 2, '2-day express delivery'),
('overnight', 'UPS', 24.99, 1, 'Next business day delivery'),
('free', 'USPS', 0.00, 7, 'Free shipping on orders over $35');

-- Sample Package Tracking
INSERT INTO package_tracking (tracking_number, carrier, status, current_location, estimated_delivery) VALUES
('TRK123456789', 'UPS', 'in_transit', 'Distribution Center, Chicago', '2024-01-18'),
('TRK987654321', 'FedEx', 'delivered', 'Customer Location, New York', '2024-01-10'),
('TRK456789123', 'USPS', 'processing', 'Warehouse Facility, Texas', '2024-01-22');
```
** **

**🎯 Features**
+ 🤝 Agent-to-Agent (A2A) Communication
+ 🧠 Persistent Session Memory & Context
+ 🗄️ Real PostgreSQL Database Integration
+ 🔄 Automated Memory Management
+ 📊 Real Products with Inventory
+ 🚀 Production-Ready Error Handling

** **

**🔧 Technical Stack**
+ AI Framework: Google ADK
+ Database: PostgreSQL (Supabase)
+ LLM: Google Gemini 2.5 Flash Lite
+ Memory: InMemoryMemoryService with persistence
+ Communication: A2A Protocol

** **
(*Learning AI Agents from Kaggle/Google's 5-Day Intensive AI Agents Course (Nov 2025)*)
** **
