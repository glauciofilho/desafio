import pandas as pd
from faker import Faker
import random
from datetime import datetime
import os
import uuid

# --- 1. Configuration ---
fake = Faker()
output_path = "./data_quality_project/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

NUM_CUSTOMERS = 15682
NUM_ORDERS = 842697
print("Generating intentionally dirty data for the quality framework challenge...")

# --- 2. Generate Customers (with some bad data) ---
customers_data = []
customer_ids = []
for i in range(NUM_CUSTOMERS):
    customer_id = str(uuid.uuid4())
    customer_ids.append(customer_id)
    email = fake.email()

    # --- Introduce NULLS ---
    if random.random() < 0.1: # 10% of customers will have a null email
        email = None

    # --- Introduce BAD FORMATS ---
    if random.random() < 0.05: # 5% of customers will have a badly formatted ID
        customer_id = f"INVALID_ID_{i}"

    customers_data.append({
        "customer_id": customer_id,
        "name": fake.name(),
        "email": email,
        "created_at": fake.date_time_this_year()
    })
df_customers = pd.DataFrame(customers_data)
df_customers.to_csv(f"{output_path}raw_customers.csv", index=False)
print(f"-> Generated {len(df_customers)} customers (with some null emails and bad IDs).")

# --- 3. Generate Orders (with more bad data) ---
orders_data = []
# --- Introduce UNEXPECTED VALUES in the set ---
valid_status = ["completed", "shipped", "returned", "cancelled"]
all_status_options = valid_status + ["pending_fraud_check", "on_hold"] # Add unexpected statuses

for _ in range(NUM_ORDERS):
    order_id = str(uuid.uuid4())
    total_price = round(random.uniform(20.0, 500.0), 2)

    # --- Introduce OUT OF RANGE VALUES ---
    if random.random() < 0.1: # 10% of orders will have a negative price
        total_price = -abs(total_price)

    orders_data.append({
        "order_id": order_id,
        "customer_id": random.choice(customer_ids),
        "order_date": fake.date_time_this_year(),
        "status": random.choice(all_status_options),
        "total_price": total_price
    })

df_orders = pd.DataFrame(orders_data)
df_orders.to_csv(f"{output_path}raw_orders.csv", index=False)
print(f"-> Generated {len(df_orders)} orders (with negative prices and unexpected statuses).")
print(f"\nDirty data generated in '{output_path}' folder.")