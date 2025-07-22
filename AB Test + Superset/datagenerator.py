import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import uuid

# --- 1. Configuration ---
fake = Faker()

# Experiment settings
NUM_USERS = 10000
EXPERIMENT_ID = "exp-new-checkout-flow-2024"
GROUPS = ["control", "variation_a", "variation_b"]
EXPERIMENT_START_DATE = datetime(2024, 5, 1)
EXPERIMENT_END_DATE = datetime(2024, 5, 31)

# Define the expected conversion rates to bake a result into the data
# variation_a should be the winner, variation_b the loser
CONVERSION_RATES = {
    "control": 0.10,      # 10% conversion rate
    "variation_a": 0.13,  # 13% conversion rate (the winner!)
    "variation_b": 0.08   # 8% conversion rate (the loser)
}

print("Starting A/B test data generation...")
output_path = "./data/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

# --- 2. Generate Users Table ---
# This table contains user attributes for segmentation.
users_data = []
user_ids = []
for i in range(NUM_USERS):
    user_id = str(uuid.uuid4())
    user_ids.append(user_id)
    users_data.append({
        "user_id": user_id,
        # User created before the experiment starts
        "created_at": fake.date_time_between(start_date="-1y", end_date=EXPERIMENT_START_DATE),
        # Attributes for segmentation
        "country": random.choice(["US", "GB", "CA", "AU", "DE"]),
        "age_group": random.choice(["18-24", "25-34", "35-44", "45+"])
    })

df_users = pd.DataFrame(users_data)
print(f"{len(df_users)} users generated.")
df_users.to_csv(f"{output_path}users.csv", index=False)

# --- 3. Generate Experiment Assignments Table ---
# This table assigns each user to a group.
assignments_data = []
for user_id in user_ids:
    group = random.choice(GROUPS)
    assignments_data.append({
        "assignment_id": str(uuid.uuid4()),
        "experiment_id": EXPERIMENT_ID,
        "user_id": user_id,
        "group_name": group,
        # Assignment happens at the beginning of the experiment window
        "assignment_date": fake.date_time_between(start_date=EXPERIMENT_START_DATE, end_date=EXPERIMENT_START_DATE + timedelta(days=2))
    })

df_assignments = pd.DataFrame(assignments_data)
print(f"{len(df_assignments)} experiment assignments generated.")
df_assignments.to_csv(f"{output_path}experiment_assignments.csv", index=False)


# --- 4. Generate Events Table (with Conversions) ---
# This table logs key user actions. We will only log the 'conversion' event for simplicity.
events_data = []
for _, assignment in df_assignments.iterrows():
    user_id = assignment['user_id']
    group = assignment['group_name']
    assignment_date = assignment['assignment_date']
    
    # Check if the user converts based on the predefined rate for their group
    conversion_rate = CONVERSION_RATES[group]
    does_convert = random.choices([True, False], weights=[conversion_rate, 1 - conversion_rate])[0]
    
    if does_convert:
        events_data.append({
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "event_name": "conversion",
            # Conversion happens after assignment and before the experiment ends
            "event_timestamp": fake.date_time_between(start_date=assignment_date, end_date=EXPERIMENT_END_DATE)
        })

df_events = pd.DataFrame(events_data)
print(f"{len(df_events)} conversion events generated.")
df_events.to_csv(f"{output_path}events.csv", index=False)

print("\n--- A/B Test Data Generation Complete ---")
print(f"Data saved in '{output_path}' folder:")
print("- users.csv")
print("- experiment_assignments.csv")
print("- events.csv")

# --- 5. Quick Sanity Check ---
# This part is for you to verify the data makes sense.
print("\n--- Sanity Check ---")
total_users_per_group = df_assignments['group_name'].value_counts()
converted_users = df_assignments[df_assignments['user_id'].isin(df_events['user_id'])]
conversions_per_group = converted_users['group_name'].value_counts()
conversion_rate_summary = (conversions_per_group / total_users_per_group).reset_index()
conversion_rate_summary.columns = ['group_name', 'observed_conversion_rate']

print("Total users per group:")
print(total_users_per_group)
print("\nObserved conversion rates (should be close to predefined rates):")
print(conversion_rate_summary)
print("\nThis confirms the data has the intended bias for your A/B test analysis.")