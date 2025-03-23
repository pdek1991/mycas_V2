import unittest
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# Set API Base URL
BASE_URL = "http://192.168.56.50:31310"

# Function to generate random data
def generate_message_id():
    return str(random.randint(10000000, 99999999))

def generate_message_text():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(characters) for _ in range(30))

def generate_device_id():
    return str(random.randint(1000000000, 9999999999))

def generate_expiry():
    future_date = datetime.now() + timedelta(days=random.randint(1, 365))
    return future_date.strftime("%Y-%m-%d")

# Function to send requests with retries
def send_request_with_retry(method, url, retries=3, timeout=5, **kwargs):
    for attempt in range(retries):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(1)  # Retry delay
            else:
                raise unittest.TestCase.failureException(f"Failed after {retries} attempts: {e}")

# Test Suite
class APITestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()

    def test_server_status(self):
        url = f"{BASE_URL}/health"
        response = send_request_with_retry("GET", url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Server is running")

    def test_generate_osm(self):
        url = f"{BASE_URL}/generate_osm"
        payload = {
            "message_id": generate_message_id(),
            "message_text": generate_message_text(),
            "device_id": generate_device_id(),
            "expiry": generate_expiry(),
        }
        response = send_request_with_retry("POST", url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Message saved successfully")

    def test_add_entitlement(self):
        url = f"{BASE_URL}/addentitlement"
        payload = {
            "device_id": generate_device_id(),
            "package_ids": "DEN_123:HW_456",
            "expiry": generate_expiry(),
        }
        response = send_request_with_retry("POST", url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Entitlements added successfully")

    def test_device_keys(self):
        url = f"{BASE_URL}/device_keys"
        payload = {
            "device_id": generate_device_id(),
            "bskeys": "7080909090",
        }
        response = send_request_with_retry("POST", url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Devices added successfully")

    @classmethod
    def tearDownClass(cls):
        elapsed_time = time.time() - cls.start_time
        print(f"\nTotal Test Execution Time: {elapsed_time:.2f} seconds")

# Load Testing Class
class LoadTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.total_requests = 0
        cls.successful_requests = 0
        cls.failed_requests = 0
        cls.response_times = []
        cls.start_time = time.time()

    def send_and_record(self, func):
        start_time = time.time()
        try:
            func()
            self.__class__.successful_requests += 1
        except Exception:
            self.__class__.failed_requests += 1
        end_time = time.time()
        self.__class__.response_times.append(end_time - start_time)
        self.__class__.total_requests += 1

    def test_concurrent_load(self):
        total_transactions = 1000
        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(total_transactions):
                executor.submit(self.send_and_record, send_generate_osm_request)
                executor.submit(self.send_and_record, send_add_entitlement_request)
                executor.submit(self.send_and_record, send_device_keys_request)

    @classmethod
    def tearDownClass(cls):
        elapsed_time = time.time() - cls.start_time
        tps = cls.total_requests / elapsed_time if elapsed_time > 0 else 0
        avg_response_time = sum(cls.response_times) / len(cls.response_times) if cls.response_times else 0
        max_response_time = max(cls.response_times) if cls.response_times else 0
        min_response_time = min(cls.response_times) if cls.response_times else 0

        print("\n==== Load Test Summary ====")
        print(f"Total Requests: {cls.total_requests}")
        print(f"Successful Requests: {cls.successful_requests}")
        print(f"Failed Requests: {cls.failed_requests}")
        print(f"Total Time Taken: {elapsed_time:.2f} seconds")
        print(f"Transactions Per Second (TPS): {tps:.2f}")
        print(f"Average Response Time: {avg_response_time:.3f} seconds")
        print(f"Max Response Time: {max_response_time:.3f} seconds")
        print(f"Min Response Time: {min_response_time:.3f} seconds")
        print("==========================")

# Request Functions
def send_generate_osm_request():
    url = f"{BASE_URL}/generate_osm"
    payload = {
        "message_id": generate_message_id(),
        "message_text": generate_message_text(),
        "device_id": generate_device_id(),
        "expiry": generate_expiry(),
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception("Request failed")

def send_add_entitlement_request():
    url = f"{BASE_URL}/addentitlement"
    payload = {
        "device_id": generate_device_id(),
        "package_ids": "DEN_123:HW_456",
        "expiry": generate_expiry(),
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception("Request failed")

def send_device_keys_request():
    url = f"{BASE_URL}/device_keys"
    payload = {
        "device_id": generate_device_id(),
        "bskeys": "7080909090",
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception("Request failed")

# Run Tests
if __name__ == "__main__":
    unittest.main()
