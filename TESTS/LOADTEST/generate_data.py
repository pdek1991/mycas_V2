import csv
import random
import string
from datetime import datetime, timedelta

# Function to generate random data for a single row
def generate_row():
    message_id = ''.join(random.choices(string.digits, k=8))
    message_text = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
    device_id = '70' + ''.join(random.choices(string.digits, k=8))
    expiry = (datetime.now() + timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    package_ids = ':'.join(['DEN_' + ''.join(random.choices(string.ascii_uppercase, k=3)) for _ in range(random.randint(1, 5))])
    bskeys = '70' + ''.join(random.choices(string.digits, k=14))

    return [message_id, message_text, device_id, expiry, package_ids, bskeys]

# Generate random data for 1000 rows
rows = [generate_row() for _ in range(1000)]

# Write data to CSV file
with open('random_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Message ID', 'Message Text', 'Device ID', 'Expiry', 'Package IDs', 'BS Keys'])
    writer.writerows(rows)

print("Random data generated and saved to 'random_data.csv'")
