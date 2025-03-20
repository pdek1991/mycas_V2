import requests
import random
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to generate a random message ID (8 digits)
def generate_message_id():
    return str(random.randint(10000000, 99999999))

# Function to generate a random message text (30 characters)
def generate_message_text():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(characters) for _ in range(30))

# Function to generate a random device ID (10 digits)
def generate_device_id():
    return str(random.randint(1000000000, 9999999999))

# Function to generate a random expiry date (future date)
def generate_expiry():
    today = datetime.now()
    future_date = today + timedelta(days=random.randint(1, 30))  # Random future date within a year
    return future_date.strftime('%Y-%m-%d')

# Function to send a request and record response time
def send_request(url, payload, endpoint_name, response_times):
    start_time = time.time()  # Record start time
    response = requests.post(url, data=payload)
    end_time = time.time()  # Record end time
    response_time = end_time - start_time  # Calculate response time
    response_times.append(response_time)  # Store response time
    print(f"{endpoint_name}, Status code: {response.status_code}, Response time: {response_time:.4f} sec")

# Function to simulate concurrent requests and collect response times
def simulate_concurrent_requests(total_transactions):
    urls = {
        "generate_osm": "http://192.168.56.50:31310/generate_osm",
        "addentitlement": "http://192.168.56.50:31310/addentitlement",
        "device_keys": "http://192.168.56.50:31310/device_keys"
    }
    
    response_times = { "generate_osm": [], "addentitlement": [], "device_keys": [] }
    total_requests = 0
    start_time = time.time()  # Record start time

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        
        for _ in range(total_transactions // 3):
            futures.append(executor.submit(send_request, urls["generate_osm"], {
                'message_id': generate_message_id(),
                'message_text': generate_message_text(),
                'device_id': generate_device_id(),
                'expiry': generate_expiry()
            }, "generate_osm", response_times["generate_osm"]))

            futures.append(executor.submit(send_request, urls["addentitlement"], {
                'device_id': generate_device_id(),
                'package_ids': 'DEN_123:HW_456',
                'expiry': generate_expiry()
            }, "addentitlement", response_times["addentitlement"]))

            futures.append(executor.submit(send_request, urls["device_keys"], {
                'device_id': generate_device_id(),
                'bskeys': '7080909090'
            }, "device_keys", response_times["device_keys"]))

            total_requests += 3
            time.sleep(0.1)  # Adjust to control request rate
        
        # Wait for all requests to finish
        for future in as_completed(futures):
            future.result()
    
    end_time = time.time()  # Record end time
    total_time_taken = end_time - start_time  # Total duration
    
    # Generate report
    print("\n--- Performance Summary ---")
    print(f"Total Requests Sent: {total_requests}")
    print(f"Total Time Taken: {total_time_taken:.2f} seconds")
    print(f"Transactions Per Second (TPS): {total_requests / total_time_taken:.2f}")

    for endpoint, times in response_times.items():
        if times:
            print(f"\n📌 {endpoint.upper()} Endpoint:")
            print(f"  🔹 Average Response Time: {sum(times) / len(times):.4f} sec")
            print(f"  🔹 Highest Response Time: {max(times):.4f} sec")
            print(f"  🔹 Lowest Response Time: {min(times):.4f} sec")
        else:
            print(f"\n📌 {endpoint.upper()} Endpoint: No responses recorded.")

# Run simulation for 1000 transactions
simulate_concurrent_requests(100)
