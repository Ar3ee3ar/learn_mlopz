import requests

def get_weather(city):
    response = requests.get(f"http://weatherapi.com/{city}")
    return response.json()


import unittest
from unittest.mock import patch

class TestWeather(unittest.TestCase):

    @patch('requests.get') # mock request.get function in get_weather named "mock_get"
    def test_get_weather(self, mock_get):
        # Define the mock response data
        mock_get.return_value.json.return_value = {
            "city": "London",
            "temperature": "20C"
        }

        # Call the function being tested
        result = get_weather("London")

        # Assert that the result is as expected
        self.assertEqual(result['city'], "London")
        self.assertEqual(result['temperature'], "20C")

        # Ensure that requests.get was called with the correct URL
        mock_get.assert_called_with("http://weatherapi.com/London")

    def test_patch_context_manager():
        # use context manager (more control over the scope of patch)
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "city": "Paris",
                "temperature": "25C"
            }

            result = get_weather("Paris")
            
            assert result['city'] == "Paris"
            assert result['temperature'] == "25C"

if __name__ == '__main__':
    unittest.main()

