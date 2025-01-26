import requests

# Base URL of the Flask app
BASE_URL = "http://localhost:8080"  # Change this if the app runs elsewhere

# Endpoint for querying the database
QUERY_ENDPOINT = f"{BASE_URL}/query"

# Example SQL query to test the database connection
query_payload = {
    "query": "SELECT * FROM your_table LIMIT 5;"  # Replace 'your_table' with an actual table name
}

try:
    # Send the POST request to the Flask app
    response = requests.post(QUERY_ENDPOINT, json=query_payload)
    
    # Check the response status code
    if response.status_code == 200:
        print("Success! Here's the response from the app:")
        print(response.json())
    else:
        print(f"Error! Status Code: {response.status_code}")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
