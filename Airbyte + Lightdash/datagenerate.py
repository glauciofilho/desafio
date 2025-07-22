import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# --- Configuration ---
fake = Faker()
output_dir = "./source_data/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

NUM_ORDERS = 31065
print("Generating source data for the Airbyte pipeline...")

# --- Generate Sales Orders ---
orders_data = []
for i in range(1, NUM_ORDERS + 1):
    order_date = fake.date_time_between(start_date="-1y", end_date="now")
    status = random.choices(["completed", "cancelled", "shipped", "preparation"], weights=[0.6, 0.1, 0.2, 0.1])[0]
    
    # Cancelled orders have no revenue
    amount = 0 if status == 'cancelled' else round(random.uniform(25.50, 499.99), 2)

    orders_data.append({
        "order_id": 1000 + i,
        "user_id": random.randint(1, 150),
        "order_date": order_date.strftime('%Y-%m-%d %H:%M:%S'),
        "status": status,
        "amount": amount
    })

df_orders = pd.DataFrame(orders_data)
file_path = os.path.join(output_dir, "sales_orders.csv")
df_orders.to_csv(file_path, index=False)

print(f"-> Generated {len(df_orders)} orders in '{file_path}'.")
print("\nSource data is ready for Airbyte.")