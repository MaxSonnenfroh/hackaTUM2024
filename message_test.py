import time
import requests

def test_message(message):
    url = "http://127.0.0.1:8000/send-message"
    response = requests.get(url, json=message)
    assert response.status_code == 200

# init the data
test_message(
{
    "key": "init",
    "value": {
        "vehicles":[
            {
                "id": "id1",
                "startCoordinate": {
                    "latitude": 48.138077, 
                    "longitude": 11.577993,
                }
            },
            {
                "id": "id2",
                "startCoordinate": {
                    "latitude": 48.138190,
                    "longitude": 11.587993,
                }
            },
            {
                "id": "id3",
                "startCoordinate": {
                    "latitude": 48.138290,
                    "longitude": 11.586093,
                }
            }

        ]
        ,
        "customer": [
            {
                "id": "id2",
                "startCoordinate": {
                    "latitude": 48.148190,
                    "longitude": 11.580000,
                },
                "destinationCoordinate": {
                    "latitude": 48.138000,
                    "longitude": 11.580000,
                }
            }
        ]
    }
}

)

time.sleep(1)

# Update the data
test_message(
    {
	"key": "update",
	"value": {
		"totalTime": "00:00:00",
		"averageWait": 4,
		"averageUtilization": 0.5,
		"loadBigger75": [
			{
				"id": "id1",
				"percentage": 0.8
			},
			{
				"id": "id2",
				"percentage": 0.9
			}
		],
		"loadSmaler25": [
			{
				"id": "id3",
				"percentage": 0.1
			},
			{
				"id": "id4",
				"percentage": 0.2
			}
		],
		"extremeWaitTime": [
			{
				"id": "id5",
				"time": "00:00:00"
			},
			{
				"id": "id6",
				"time": "00:00:00"
			}
		],
		"waitingCustomers": ["id3", "id4"],
		"customersOnTransit": ["id1", "id2"],
		"dropedCustomers": ["id5", "id6"],
		"currentDistance": {
			"id1": 5,
			"id2": 5,
			"id3": 5,
			"id4": 5,
			"id5": 5,
			"id6": 5
		}
	}
}

)
