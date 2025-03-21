import requests

# Define the base URL with the node IP and NodePort
base_url = "http://192.168.56.50:31310"

# Define the endpoint paths
endpoints = ["/health"]

# Iterate over each endpoint and make a request
for endpoint in endpoints:
    url = "http://192.168.56.50:31310/health"
    response = requests.get(url)  # Modify the data payload as needed
    print(f"Endpoint: {endpoint}, Status code: {response.status_code}")

    # Optionally, print response content
    print(response.text)
