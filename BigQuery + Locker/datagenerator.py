import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import uuid

# --- 1. Configuration ---
fake = Faker()
output_path = "./data_modern_stack/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Number of records
NUM_CUSTOMERS = 4853
NUM_PRODUCTS = 1000
NUM_ORDERS = 35149
NUM_TICKETS = 4218

# Time window for the data
DATA_START_DATE = datetime(2022, 1, 1)
DATA_END_DATE = datetime.now()

print("Starting realistic data generation for Shopify, Stripe, and Zendesk...")

# --- 2. Generate Shopify Products ---
products_data = []
product_ids = []
for i in range(NUM_PRODUCTS):
    product_id = str(uuid.uuid4())
    product_ids.append(product_id)
    products_data.append({
        "id": product_id,
        "name": f"{fake.color_name().capitalize()} {fake.word().capitalize()} {random.choice(['Kit', 'Box', 'Set', 'Accessory'])}",
        "price": round(random.uniform(10.0, 200.0), 2),
        "created_at": fake.date_time_between(start_date="-3y", end_date=DATA_START_DATE)
    })
df_products = pd.DataFrame(products_data)
df_products.to_csv(f"{output_path}raw_shopify_products.csv", index=False)
print(f"-> Generated {len(df_products)} Shopify products.")

# --- 3. Generate Shopify Customers ---
customers_data = []
for _ in range(NUM_CUSTOMERS):
    customers_data.append({
        "id": str(uuid.uuid4()),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "created_at": fake.date_time_between(start_date=DATA_START_DATE, end_date=DATA_END_DATE)
    })
df_customers = pd.DataFrame(customers_data)
df_customers.to_csv(f"{output_path}raw_shopify_customers.csv", index=False)
print(f"-> Generated {len(df_customers)} Shopify customers.")

# --- 4. Generate Shopify Orders and Line Items ---
orders_data = []
line_items_data = []
order_status_options = ["fulfilled", "fulfilled", "fulfilled", "returned", "cancelled"] # Higher chance of being fulfilled

for _ in range(NUM_ORDERS):
    order_id = str(uuid.uuid4())
    customer = df_customers.sample(1).iloc[0]
    order_date = fake.date_time_between(start_date=customer['created_at'], end_date=DATA_END_DATE)
    order_total = 0

    # Each order has 1 to 4 line items
    for _ in range(random.randint(1, 4)):
        product = df_products.sample(1).iloc[0]
        quantity = random.randint(1, 3)
        line_item_price = product['price'] * quantity
        order_total += line_item_price

        line_items_data.append({
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "product_id": product['id'],
            "quantity": quantity,
            "price": product['price']
        })

    orders_data.append({
        "id": order_id,
        "customer_id": customer['id'],
        "created_at": order_date,
        "status": random.choice(order_status_options),
        "total_price": round(order_total, 2)
    })

df_orders = pd.DataFrame(orders_data)
df_line_items = pd.DataFrame(line_items_data)
df_orders.to_csv(f"{output_path}raw_shopify_orders.csv", index=False)
df_line_items.to_csv(f"{output_path}raw_shopify_line_items.csv", index=False)
print(f"-> Generated {len(df_orders)} Shopify orders and {len(df_line_items)} line items.")

# --- 5. Generate Stripe Charges ---
# Charges are only created for orders that were not cancelled
charges_data = []
successful_orders = df_orders[df_orders['status'] != 'cancelled']

for _, order in successful_orders.iterrows():
    charges_data.append({
        "id": f"ch_{uuid.uuid4().hex[:24]}", # Mimic Stripe charge ID format
        "amount": int(order['total_price'] * 100), # Stripe amount is in cents
        "status": "succeeded" if order['status'] != 'returned' else 'refunded',
        "order_id": order['id'], # Custom metadata to link to Shopify
        "created": order['created_at'] + timedelta(seconds=random.randint(10, 300))
    })
df_charges = pd.DataFrame(charges_data)
df_charges.to_csv(f"{output_path}raw_stripe_charges.csv", index=False)
print(f"-> Generated {len(df_charges)} Stripe charges.")

# --- 6. Generate Zendesk Tickets ---
tickets_data = []
# Get customers who had returned orders - they are more likely to complain
returned_order_customers = df_orders[df_orders['status'] == 'returned']['customer_id'].unique()

for _ in range(NUM_TICKETS):
    # 50% chance the ticket comes from a customer with a returned order
    if random.random() < 0.5 and len(returned_order_customers) > 0:
        customer_id = random.choice(returned_order_customers)
    else:
        customer_id = df_customers.sample(1).iloc[0]['id']

    customer_created_at = df_customers[df_customers['id'] == customer_id]['created_at'].iloc[0]

    tickets_data.append({
        "id": random.randint(10000, 99999),
        "requester_id": customer_id, # This is the link to the Shopify customer
        "subject": fake.sentence(nb_words=6),
        "status": random.choice(["open", "solved", "solved", "closed"]),
        "priority": random.choice(["low", "normal", "normal", "high"]),
        "created_at": fake.date_time_between(start_date=customer_created_at, end_date=DATA_END_DATE)
    })

df_tickets = pd.DataFrame(tickets_data)
df_tickets.to_csv(f"{output_path}raw_zendesk_tickets.csv", index=False)
print(f"-> Generated {len(df_tickets)} Zendesk tickets.")

print(f"\nRealistic data generation complete. Files are in '{output_path}'.")