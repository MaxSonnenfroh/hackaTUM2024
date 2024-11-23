import requests

def test_message(message):
    url = "http://127.0.0.1:8000/send-message"
    response = requests.get(url, json=message)
    assert response.status_code == 200

# Run the test
test_message({"message": "Hello, World!"})
# Output: {"message": "Hello, World!"}
test_message({"message": "Goodbye, World!"})