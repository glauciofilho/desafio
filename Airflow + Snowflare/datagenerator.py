import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# --- 1. Configuration ---
# Initialize Faker to generate English data
fake = Faker()

# Define the number of records to generate
NUM_CUSTOMERS = 10000
NUM_INVOICES = 120000
NUM_CAMPAIGN_INTERACTIONS = 65752

print("Starting data generation process...")

# --- NEW STEP: Load the real US cities data ---
try:
    locations_df = pd.read_csv("us_cities.csv")
    print("Successfully loaded us_cities.csv for realistic location data.")
except FileNotFoundError:
    print("Error: 'us_cities.csv' not found. Please create the file with city and state data.")
    exit() # Exit the script if the reference file is missing

# --- 2. Generate CRM Data (Customers Table) ---
customers_data = []
customer_ids = []

for i in range(1, NUM_CUSTOMERS + 1):
    customer_id = f"CUST-{i:04d}"
    customer_ids.append(customer_id)
    
    join_date = fake.date_between(start_date='-2y', end_date='today')
    
    # --- MODIFIED SECTION: Get a realistic city and state pair ---
    random_location = locations_df.sample(n=1).iloc[0]
    city = random_location['city']
    state = random_location['state_id']
    
    customers_data.append({
        "customer_id": customer_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "city": city,    # Use the realistic city
        "state": state,  # Use the corresponding state
        "join_date": join_date
    })

df_customers = pd.DataFrame(customers_data)
print(f"{len(df_customers)} customer records generated.")

# --- 3. Generate Sales Data (Invoices Table) ---
# (This section remains unchanged, as it depends on customer_id, not location)
invoices_data = []
invoice_status_options = ["paid", "pending", "cancelled"]

for i in range(1, NUM_INVOICES + 1):
    customer_id = random.choice(customer_ids)
    customer_join_date = df_customers[df_customers['customer_id'] == customer_id]['join_date'].iloc[0]
    invoice_date = fake.date_between(start_date=customer_join_date, end_date='today')
    
    invoices_data.append({
        "invoice_id": f"INV-{i:05d}",
        "customer_id": customer_id,
        "invoice_date": invoice_date,
        "amount": round(random.uniform(20.5, 500.0), 2),
        "status": random.choice(invoice_status_options)
    })

df_invoices = pd.DataFrame(invoices_data)
print(f"{len(df_invoices)} invoice records generated.")

# --- 4. Generate Marketing Campaign Data ---
# (This section also remains unchanged)
campaigns_data = []
campaign_names = ["Holiday_Sale_2024", "Black_Friday_2024", "Spring_Promo_2025", "Summer_Clearance_2024"]
interaction_types = ["opened", "clicked", "unsubscribed"]

for i in range(1, NUM_CAMPAIGN_INTERACTIONS + 1):
    customer_id = random.choice(customer_ids)
    customer_join_date = df_customers[df_customers['customer_id'] == customer_id]['join_date'].iloc[0]
    event_date = fake.date_time_between(start_date=customer_join_date, end_date='now', tzinfo=None)

    campaigns_data.append({
        "event_id": f"EVT-{i:06d}",
        "customer_id": customer_id,
        "campaign_name": random.choice(campaign_names),
        "event_date": event_date.strftime('%Y-%m-%d %H:%M:%S'),
        "interaction_type": random.choice(interaction_types)
    })

df_campaigns = pd.DataFrame(campaigns_data)
print(f"{len(df_campaigns)} campaign interaction records generated.")

# --- 5. Save DataFrames to CSV files ---
output_path = "./data/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

df_customers.to_csv(f"{output_path}crm_customers.csv", index=False)
df_invoices.to_csv(f"{output_path}sales_invoices.csv", index=False)
df_campaigns.to_csv(f"{output_path}marketing_campaigns.csv", index=False)

print("\nCSV files generated successfully in the 'data' folder:")
print(f"- {output_path}crm_customers.csv")
print(f"- {output_path}sales_invoices.csv")
print(f"- {output_path}marketing_campaigns.csv")